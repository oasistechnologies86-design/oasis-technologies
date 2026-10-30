from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash

from .config import get_settings

password_hash = PasswordHash.recommended()
bearer_scheme = HTTPBearer(auto_error=False)
ALGORITHM = "HS256"


def create_access_token(subject: str) -> str:
    settings = get_settings()
    if len(settings.jwt_secret.encode("utf-8")) < 32:
        raise HTTPException(status_code=503, detail="Admin authentication is not configured.")
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_minutes)
    return jwt.encode({"sub": subject, "exp": expires, "iat": datetime.now(timezone.utc)}, settings.jwt_secret, algorithm=ALGORITHM)


def require_admin(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> str:
    settings = get_settings()
    if not credentials:
        raise HTTPException(status_code=401, detail="Sign in to access this resource.", headers={"WWW-Authenticate": "Bearer"})
    if len(settings.jwt_secret.encode("utf-8")) < 32:
        raise HTTPException(status_code=503, detail="Admin authentication is not configured.")
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=[ALGORITHM])
        subject = payload.get("sub")
        if not subject or subject.casefold() != settings.admin_email.casefold():
            raise ValueError("Unexpected token subject")
        return subject
    except (jwt.InvalidTokenError, ValueError):
        raise HTTPException(status_code=401, detail="Your session is invalid or expired. Please sign in again.", headers={"WWW-Authenticate": "Bearer"})
