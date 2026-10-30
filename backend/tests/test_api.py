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
