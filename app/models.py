from pydantic import BaseModel, EmailStr, Field

class UserRegistered(BaseModel):
    email: EmailStr
    name: str = Field(min_length=2)
    phone: str | None = None
