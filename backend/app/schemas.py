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
