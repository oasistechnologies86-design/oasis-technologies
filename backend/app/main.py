import logging
from contextlib import asynccontextmanager
from datetime import timezone

from fastapi import Depends, FastAPI, HTTPException
from pwdlib.exceptions import UnknownHashError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .config import get_settings
from .database import Base, engine, get_db
from .models import ContactEnquiry, Service, SiteSettings
from .schemas import AdminLogin, AdminToken, ContactCreate, ContactCreated, EnquiryStatusUpdate, ServiceCreate, ServiceUpdate, SiteSettingsUpdate
from .security import create_access_token, password_hash, require_admin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("oasis")
settings = get_settings()
SERVICES = [
    {"slug": "software-development", "title": "Software development", "description": "Purpose-built business applications and digital products."},
    {"slug": "web-mobile-apps", "title": "Web & mobile apps", "description": "Accessible digital experiences across devices."},
    {"slug": "it-consulting", "title": "IT consulting", "description": "Technology strategy and practical guidance."},
    {"slug": "cloud-deployment", "title": "Cloud & deployment", "description": "Cloud foundations and scalable infrastructure."},
    {"slug": "it-support", "title": "IT support & maintenance", "description": "Technical assistance and ongoing application care."},
    {"slug": "api-integrations", "title": "API & integrations", "description": "Connect tools with secure APIs and automation."},
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create any missing tables on every environment, including Render production.
    # SQLAlchemy create_all is additive: it creates absent tables but does not
    # rename, alter, or delete existing tables/columns. Use a versioned migration
    # for future changes to an existing table's structure.
    Base.metadata.create_all(bind=engine)
    # Safe additive migration for existing databases: preserve all prior enquiries.
    inspector = inspect(engine)
    if inspector.has_table("contact_enquiries") and "phone" not in {column["name"] for column in inspector.get_columns("contact_enquiries")}:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE contact_enquiries ADD COLUMN phone VARCHAR(40)"))
    with engine.begin() as connection:
        existing_services = connection.execute(text("SELECT COUNT(*) FROM services")).scalar_one()
        if existing_services == 0:
            for index, service in enumerate(SERVICES):
                connection.execute(
                    text("INSERT INTO services (slug, title, description, active, sort_order) VALUES (:slug, :title, :description, :active, :sort_order)"),
                    {**service, "active": True, "sort_order": index},
                )
    yield


app = FastAPI(title="Oasis Technologies API", version="0.2.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/")
def root():
    return {"name": "Oasis Technologies API", "version": app.version, "docs": "/docs"}


@app.get("/api/v1/health")
def health():
    return {"status": "ok", "environment": settings.app_env}


@app.get("/api/v1/health/ready")
def readiness(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        logger.exception("Readiness check failed")
        raise HTTPException(status_code=503, detail="Database is not ready")
    return {"status": "ready"}


def _service_payload(row: Service):
    return {"id": row.id, "slug": row.slug, "title": row.title, "description": row.description, "active": row.active, "sort_order": row.sort_order}


@app.get("/api/v1/services")
def list_services(db: Session = Depends(get_db)):
    rows = db.query(Service).filter(Service.active.is_(True)).order_by(Service.sort_order, Service.id).all()
    return {"items": [_service_payload(row) for row in rows]}


@app.get("/api/v1/services/{slug}")
def get_service(slug: str, db: Session = Depends(get_db)):
    row = db.query(Service).filter(Service.slug == slug, Service.active.is_(True)).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return _service_payload(row)


@app.get("/api/v1/admin/services")
def admin_list_services(_: str = Depends(require_admin), db: Session = Depends(get_db)):
    rows = db.query(Service).order_by(Service.sort_order, Service.id).all()
    return {"items": [_service_payload(row) for row in rows]}


@app.post("/api/v1/admin/services", status_code=201)
def admin_create_service(payload: ServiceCreate, _: str = Depends(require_admin), db: Session = Depends(get_db)):
    import re
    import time
    slug = re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", payload.title.casefold())).strip("-")[:140] or "service"
    if db.query(Service).filter(Service.slug == slug).first():
        slug = f"{slug}-{int(time.time())}"
    item = Service(slug=slug, title=payload.title.strip(), description=payload.description.strip(), active=payload.active, sort_order=payload.sort_order)
    db.add(item)
    try:
        db.commit()
        db.refresh(item)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Unable to create service")
        raise HTTPException(status_code=503, detail="Unable to create service. Please try again.")
    return _service_payload(item)


@app.put("/api/v1/admin/services/{service_id}")
def admin_update_service(service_id: int, payload: ServiceUpdate, _: str = Depends(require_admin), db: Session = Depends(get_db)):
    item = db.get(Service, service_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Service not found.")
    item.title = payload.title.strip()
    item.description = payload.description.strip()
    item.active = payload.active
    item.sort_order = payload.sort_order
    try:
        db.commit()
        db.refresh(item)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Unable to update service")
        raise HTTPException(status_code=503, detail="Unable to update service. Please try again.")
    return _service_payload(item)


@app.delete("/api/v1/admin/services/{service_id}")
def admin_delete_service(service_id: int, _: str = Depends(require_admin), db: Session = Depends(get_db)):
    item = db.get(Service, service_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Service not found.")
    # Soft-delete so historic enquiries retain their service label and records.
    item.active = False
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Unable to archive service")
        raise HTTPException(status_code=503, detail="Unable to archive service. Please try again.")
    return {"id": item.id, "active": False}


@app.post("/api/v1/contact", response_model=ContactCreated, status_code=201)
def create_contact(payload: ContactCreate, db: Session = Depends(get_db)):
    item = ContactEnquiry(
        name=payload.name,
        email=str(payload.email),
        phone=payload.phone.strip(),
        company=payload.company.strip() if payload.company else None,
        service=payload.service,
        message=payload.message,
    )
    db.add(item)
    try:
        db.commit()
        db.refresh(item)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Unable to save contact enquiry")
        raise HTTPException(status_code=503, detail="We could not save your message. Please try again later.")
    logger.info("Contact enquiry received id=%s", item.id)
    return ContactCreated(id=item.id, message="Thank you. Your enquiry has been received.")


@app.post("/api/v1/auth/login", response_model=AdminToken)
def admin_login(payload: AdminLogin):
    email = str(payload.email).strip().casefold()
    if not settings.admin_email or not settings.admin_password_hash or len(settings.jwt_secret.encode("utf-8")) < 32:
        raise HTTPException(status_code=503, detail="Admin authentication is not configured. Contact the site administrator.")
    # Always run a password verification when configured to reduce account-enumeration timing differences.
    valid_password = False
    try:
        valid_password = password_hash.verify(payload.password, settings.admin_password_hash)
    except (UnknownHashError, ValueError, TypeError):
        logger.error("Configured admin password hash is invalid.")
    if email != settings.admin_email.strip().casefold() or not valid_password:
        raise HTTPException(status_code=401, detail="Email or password is incorrect.")
    token = create_access_token(settings.admin_email.strip())
    return AdminToken(access_token=token, expires_in=settings.jwt_access_token_minutes * 60)


@app.get("/api/v1/admin/enquiries")
def admin_enquiries(_: str = Depends(require_admin), db: Session = Depends(get_db)):
    rows = db.query(ContactEnquiry).order_by(ContactEnquiry.created_at.desc(), ContactEnquiry.id.desc()).limit(250).all()
    return {
        "items": [
            {
                "id": row.id,
                "name": row.name,
                "email": row.email,
                "phone": row.phone,
                "company": row.company,
                "service": row.service,
                "message": row.message,
                "status": row.status,
                "created_at": row.created_at.replace(tzinfo=timezone.utc).isoformat() if row.created_at.tzinfo is None else row.created_at.isoformat(),
            }
            for row in rows
        ]
    }


@app.patch("/api/v1/admin/enquiries/{enquiry_id}")
def update_enquiry_status(
    enquiry_id: int,
    payload: EnquiryStatusUpdate,
    _: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    item = db.get(ContactEnquiry, enquiry_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Enquiry not found.")
    item.status = payload.status
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Unable to update enquiry status")
        raise HTTPException(status_code=503, detail="Unable to update enquiry. Please try again.")
    return {"id": item.id, "status": item.status}


def _site_settings_payload(row: SiteSettings):
    return {
        "company_name": row.company_name,
        "contact_email": row.contact_email,
        "phone_primary": row.phone_primary,
        "phone_secondary": row.phone_secondary,
        "tagline": row.tagline,
        "hero_title": row.hero_title,
        "hero_accent": row.hero_accent,
        "hero_description": row.hero_description,
    }


def _get_or_create_site_settings(db: Session) -> SiteSettings:
    row = db.get(SiteSettings, 1)
    if row is None:
        row = SiteSettings(id=1)
        db.add(row)
        db.commit()
        db.refresh(row)
    return row


@app.get("/api/v1/site-settings")
def public_site_settings(db: Session = Depends(get_db)):
    return _site_settings_payload(_get_or_create_site_settings(db))


@app.get("/api/v1/admin/site-settings")
def admin_site_settings(_: str = Depends(require_admin), db: Session = Depends(get_db)):
    return _site_settings_payload(_get_or_create_site_settings(db))


@app.put("/api/v1/admin/site-settings")
def update_site_settings(payload: SiteSettingsUpdate, _: str = Depends(require_admin), db: Session = Depends(get_db)):
    row = _get_or_create_site_settings(db)
    for field, value in payload.model_dump().items():
        setattr(row, field, str(value))
    try:
        db.commit()
        db.refresh(row)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Unable to update website settings")
        raise HTTPException(status_code=503, detail="Unable to save website settings. Please try again.")
    return _site_settings_payload(row)
