import os

os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///./test_oasis.db"
os.environ["CORS_ORIGINS"] = "http://localhost:5173"

from fastapi.testclient import TestClient
from pwdlib import PasswordHash

from app.config import get_settings
from app.main import app
from app.database import Base, engine

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
client = TestClient(app)


def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200 and response.json()["status"] == "ok"


def test_services():
    response = client.get("/api/v1/services")
    assert response.status_code == 200 and len(response.json()["items"]) >= 1


def test_contact_validation():
    response = client.post("/api/v1/contact", json={"name": "A", "email": "bad", "service": "IT", "message": "short"})
    assert response.status_code == 422


def test_contact_submission():
    response = client.post("/api/v1/contact", json={"name": "Test Customer", "email": "customer@example.com", "company": "Example Ltd", "service": "Software development", "message": "I would like to discuss a business application."})
    assert response.status_code == 201 and response.json()["id"] > 0


def test_admin_requires_authentication():
    assert client.get("/api/v1/admin/enquiries").status_code == 401


def test_admin_login_and_enquiry_access():
    settings = get_settings()
    settings.admin_email = "admin@example.com"
    settings.admin_password_hash = PasswordHash.recommended().hash("Test-Only-Strong-Password-123!")
    settings.jwt_secret = "test-secret-value-with-at-least-thirty-two-bytes"
    login = client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "Test-Only-Strong-Password-123!"})
    assert login.status_code == 200
    token = login.json()["access_token"]
    response = client.get("/api/v1/admin/enquiries", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "items" in response.json()


def test_admin_rejects_bad_password():
    settings = get_settings()
    settings.admin_email = "admin@example.com"
    settings.admin_password_hash = PasswordHash.recommended().hash("Test-Only-Strong-Password-123!")
    settings.jwt_secret = "test-secret-value-with-at-least-thirty-two-bytes"
    response = client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "wrong-password"})
    assert response.status_code == 401



def test_admin_login_invalid_hash_returns_401_not_500():
    settings = get_settings()
    settings.admin_email = "admin@example.com"
    settings.admin_password_hash = "not-a-valid-password-hash"
    settings.jwt_secret = "test-secret-value-with-at-least-thirty-two-bytes"
    response = client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "any-password"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Email or password is incorrect."


def test_production_frontend_cors_preflight():
    response = client.options(
        "/api/v1/auth/login",
        headers={
            "Origin": "https://oasis-technologies-pearl.vercel.app",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "https://oasis-technologies-pearl.vercel.app"


def test_public_site_settings_has_contact_details():
    response = client.get("/api/v1/site-settings")
    assert response.status_code == 200
    data = response.json()
    assert data["contact_email"] == "oasistechnologies86@gmail.com"
    assert data["phone_primary"] == "0246470941"
    assert data["phone_secondary"] == "0201491597"


def test_site_settings_admin_authentication_and_update():
    settings = get_settings()
    settings.admin_email = "admin@example.com"
    settings.admin_password_hash = PasswordHash.recommended().hash("Test-Only-Strong-Password-123!")
    settings.jwt_secret = "test-secret-value-with-at-least-thirty-two-bytes"
    payload = {
        "company_name": "Oasis Technologies",
        "contact_email": "oasistechnologies86@gmail.com",
        "phone_primary": "0246470941",
        "phone_secondary": "0201491597",
        "tagline": "Thoughtful technology. Real-world impact.",
        "hero_title": "Build what is next.",
        "hero_accent": "Make it matter.",
        "hero_description": "We build digital products and deliver reliable IT services to help businesses move forward.",
    }
    assert client.put("/api/v1/admin/site-settings", json=payload).status_code == 401
    login = client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "Test-Only-Strong-Password-123!"})
    assert login.status_code == 200
    token = login.json()["access_token"]
    response = client.put("/api/v1/admin/site-settings", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert client.get("/api/v1/site-settings").json()["contact_email"] == payload["contact_email"]
