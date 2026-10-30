from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


class ContactCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    company: str | None = Field(default=None, max_length=160)
    service: str = Field(min_length=2, max_length=120)
    message: str = Field(min_length=10, max_length=5000)

    @field_validator("name", "service", "message")
    @classmethod
    def strip_text(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be empty.")
        return value


class ContactCreated(BaseModel):
    id: int
    message: str


class AdminLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=1024)


class AdminToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class EnquiryStatusUpdate(BaseModel):
    status: Literal["new", "in_progress", "resolved"]


class SiteSettingsUpdate(BaseModel):
    company_name: str = Field(min_length=2, max_length=120)
    contact_email: EmailStr
    phone_primary: str = Field(min_length=7, max_length=40)
    phone_secondary: str = Field(min_length=7, max_length=40)
    tagline: str = Field(min_length=2, max_length=240)
    hero_title: str = Field(min_length=2, max_length=120)
    hero_accent: str = Field(min_length=2, max_length=120)
    hero_description: str = Field(min_length=10, max_length=1000)

    @field_validator("company_name", "phone_primary", "phone_secondary", "tagline", "hero_title", "hero_accent", "hero_description")
    @classmethod
    def strip_site_text(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be empty.")
        return value
