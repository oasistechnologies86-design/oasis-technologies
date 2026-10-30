from datetime import datetime, timezone
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base
def utcnow():
    return datetime.now(timezone.utc)
class ContactEnquiry(Base):
    __tablename__ = "contact_enquiries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    company: Mapped[str | None] = mapped_column(String(160), nullable=True)
    service: Mapped[str] = mapped_column(String(120), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="new")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class SiteSettings(Base):
    __tablename__ = "site_settings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    company_name: Mapped[str] = mapped_column(String(120), nullable=False, default="Oasis Technologies")
    contact_email: Mapped[str] = mapped_column(String(254), nullable=False, default="oasistechnologies86@gmail.com")
    phone_primary: Mapped[str] = mapped_column(String(40), nullable=False, default="0246470941")
    phone_secondary: Mapped[str] = mapped_column(String(40), nullable=False, default="0201491597")
    tagline: Mapped[str] = mapped_column(String(240), nullable=False, default="Thoughtful technology. Real-world impact.")
    hero_title: Mapped[str] = mapped_column(String(120), nullable=False, default="Build what's next.")
    hero_accent: Mapped[str] = mapped_column(String(120), nullable=False, default="Make it matter.")
    hero_description: Mapped[str] = mapped_column(Text, nullable=False, default="We build useful digital products and deliver dependable IT services that help ambitious businesses move forward.")


class Service(Base):
    __tablename__ = "services"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(140), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    active: Mapped[bool] = mapped_column(default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
