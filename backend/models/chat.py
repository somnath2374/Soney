from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ChatMessage(BaseModel):
    id: Optional[str] = Field(alias="_id")
    sender_id: str
    receiver_id: str
    message: str
    timestamp: Optional[datetime] = datetime.utcnow()
    read: bool = False

class ChatCreate(BaseModel):
    receiver_id: str
    message: str

class ChatResponse(BaseModel):
    sender_id: str
    receiver_id: str
    message: str
    timestamp: datetime
    read: bool

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
