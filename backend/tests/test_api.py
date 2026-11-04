import os

os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///./test_oasis.db"
os.environ["CORS_ORIGINS"] = "http://localhost:5173"

from fastapi.testclient import TestClient
from pwdlib import PasswordHash
from sqlalchemy import create_engine, inspect, text

from app.config import get_settings
from app.main import app, _apply_additive_migrations, _seed_services
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
    response = client.post("/api/v1/contact", json={"name": "Test Customer", "email": "customer@example.com", "phone": "+233241234567", "company": "Example Ltd", "service": "Software development", "message": "I would like to discuss a business application."})
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


def test_lifespan_startup_seeds_services_and_serves_them():
    """A fresh database must start cleanly and expose the seeded catalog.

    TestClient is used as a context manager so the FastAPI lifespan runs. The
    earlier startup bug (a raw INSERT omitting the NOT NULL created_at column)
    only appeared when the lifespan executed, which the other tests never did.
    """
    with TestClient(app) as startup_client:
        response = startup_client.get("/api/v1/services")
        assert response.status_code == 200
        assert len(response.json()["items"]) >= 1


def test_additive_migration_upgrades_pre_services_release_schema(tmp_path):
    """A database from a release that predates the service columns is upgraded.

    create_all cannot add columns to an existing table, so without the additive
    migration every query touching the services table returned HTTP 500.
    """
    db_path = tmp_path / "legacy.db"
    legacy_engine = create_engine(f"sqlite:///{db_path}")
    with legacy_engine.begin() as connection:
        connection.execute(text(
            "CREATE TABLE services (id INTEGER PRIMARY KEY, slug VARCHAR(140) UNIQUE NOT NULL, "
            "title VARCHAR(120) NOT NULL, description TEXT NOT NULL)"
        ))
        connection.execute(text(
            "INSERT INTO services (slug, title, description) "
            "VALUES ('software-development', 'Software development', 'Legacy row')"
        ))

    _apply_additive_migrations(legacy_engine)
    _seed_services(legacy_engine)

    columns = {column["name"] for column in inspect(legacy_engine).get_columns("services")}
    assert {"active", "sort_order", "created_at"} <= columns
    with legacy_engine.begin() as connection:
        rows = connection.execute(text("SELECT title, description, active, sort_order, created_at FROM services")).all()
    assert len(rows) == 1
    assert rows[0][0] == "Software development"
    assert rows[0][1] == "Legacy row"
    assert rows[0][2] in (True, 1)
