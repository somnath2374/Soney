from pydantic import BaseModel, Field
from typing import Optional

class Comment(BaseModel):
    id: Optional[str] = Field(alias="_id")
    post_id: str
    author_id: str
    content: str
    created_at: Optional[str]

class CommentCreate(BaseModel):
    post_id: str
    author_id: str
    content: str

class CommentResponse(BaseModel):
    id: str
    post_id: str
    author_id: str
    content: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
