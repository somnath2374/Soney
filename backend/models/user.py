from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from bson import ObjectId
from typing import List

class User(BaseModel):
    id: Optional[str] = Field(alias="_id")
    username: str
    email: EmailStr
    hashed_password: str
    is_active: bool = True
    created_at: Optional[str]
    updated_at: Optional[str]
    friends: List[str] = []
    friend_requests: List[str] = []

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    friends: List[str]
    friend_requests: List[str]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
