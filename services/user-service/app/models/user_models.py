from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    phone: str = Field(..., regex=r"^\+?[1-9]\d{1,14}$")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    phone: Optional[str] = Field(None, regex=r"^\+?[1-9]\d{1,14}$")
    password: Optional[str] = Field(None, min_length=8)

class UserInDB(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
    status: str