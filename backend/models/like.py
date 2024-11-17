from pydantic import BaseModel, Field
from typing import Optional

class Like(BaseModel):
    id: Optional[str] = Field(alias="_id")
    post_id: str
    user_id: str
    created_at: Optional[str]

class LikeCreate(BaseModel):
    post_id: str
    user_id: str

class LikeResponse(BaseModel):
    id: str
    post_id: str
    user_id: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
