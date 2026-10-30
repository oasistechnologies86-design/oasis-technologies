import logging
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from .config import get_settings
from .database import Base, engine, get_db
from .models import ContactEnquiry
from .schemas import ContactCreate, ContactCreated

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("oasis")
settings = get_settings()
SERVICES = [
 {"slug":"software-development","title":"Software development","description":"Purpose-built business applications and digital products."},
 {"slug":"web-mobile-apps","title":"Web & mobile apps","description":"Accessible digital experiences across devices."},
 {"slug":"it-consulting","title":"IT consulting","description":"Technology strategy and practical guidance."},
 {"slug":"cloud-deployment","title":"Cloud & deployment","description":"Cloud foundations and scalable infrastructure."},
 {"slug":"it-support","title":"IT support & maintenance","description":"Technical assistance and ongoing application care."},
 {"slug":"api-integrations","title":"API & integrations","description":"Connect tools with secure APIs and automation."}
]
@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.app_env.lower() in {"development","local","test"}:
        Base.metadata.create_all(bind=engine)
    yield
app = FastAPI(title="Oasis Technologies API", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins, allow_credentials=False, allow_methods=["GET","POST","OPTIONS"], allow_headers=["Content-Type"])
@app.get("/")
def root():
    return {"name":"Oasis Technologies API","version":app.version,"docs":"/docs"}
@app.get("/api/v1/health")
def health():
    return {"status":"ok","environment":settings.app_env}
@app.get("/api/v1/health/ready")
def readiness(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        logger.exception("Readiness check failed")
        raise HTTPException(status_code=503, detail="Database is not ready")
    return {"status":"ready"}
@app.get("/api/v1/services")
def list_services():
    return {"items":SERVICES}
@app.get("/api/v1/services/{slug}")
def get_service(slug: str):
    for service in SERVICES:
        if service["slug"] == slug:
            return service
    raise HTTPException(status_code=404, detail="Service not found")
@app.post("/api/v1/contact", response_model=ContactCreated, status_code=201)
def create_contact(payload: ContactCreate, db: Session = Depends(get_db)):
    item = ContactEnquiry(name=payload.name,email=str(payload.email),company=payload.company.strip() if payload.company else None,service=payload.service,message=payload.message)
    db.add(item)
    try:
        db.commit()
        db.refresh(item)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Unable to save contact enquiry")
        raise HTTPException(status_code=503, detail="We could not save your message. Please try again later.")
    logger.info("Contact enquiry received id=%s", item.id)
    return ContactCreated(id=item.id,message="Thank you. Your enquiry has been received.")
@app.get("/api/v1/admin/enquiries")
def admin_enquiries():
    raise HTTPException(status_code=501, detail="Admin API is disabled until authentication and role-based access are implemented.")
