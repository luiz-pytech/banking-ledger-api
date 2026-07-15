from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
import uuid


class UserCreate(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    document: str = Field(min_length=11, max_length=20,
                          description="User's document number")
    email: EmailStr
    password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=3, max_length=120)
    document: Optional[str] = Field(
        default=None, min_length=11, max_length=20, description="User's document number")
    email: Optional[EmailStr] = Field(default=None)


class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    document: str = Field(min_length=11, max_length=20,
                          description="User's document number")
    email: EmailStr

    model_config = {"from_attributes": True}


class UserDelete(BaseModel):
    id: uuid.UUID


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
