from pydantic import BaseModel, EmailStr
from typing import Optional, List

class HoneytrapCreate(BaseModel):
    purpose: str

class HoneytrapResponse(BaseModel):
    id: str
    purpose: str
    username: str
    email: EmailStr
    friends: List[str] = []
    friend_requests: List[str] = []

    class Config:
        orm_mode = True
        allow_population_by_field_name = True