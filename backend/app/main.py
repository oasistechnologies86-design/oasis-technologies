import logging
from contextlib import asynccontextmanager
from datetime import timezone

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .config import get_settings
from .database import Base, engine, get_db
from .models import ContactEnquiry, SiteSettings
from .schemas import AdminLogin, AdminToken, ContactCreate, ContactCreated, EnquiryStatusUpdate, SiteSettingsUpdate
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
    yield


app = FastAPI(title="Oasis Technologies API", version="0.2.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
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


@app.get("/api/v1/services")
def list_services():
    return {"items": SERVICES}


@app.get("/api/v1/services/{slug}")
def get_service(slug: str):
    for service in SERVICES:
        if service["slug"] == slug:
            return service
    raise HTTPException(status_code=404, detail="Service not found")


@app.post("/api/v1/contact", response_model=ContactCreated, status_code=201)
def create_contact(payload: ContactCreate, db: Session = Depends(get_db)):
    item = ContactEnquiry(
        name=payload.name,
        email=str(payload.email),
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
    except (ValueError, TypeError):
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
