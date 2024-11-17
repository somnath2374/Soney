from pydantic import BaseModel, Field
from models.comment import Comment
from typing import Optional, List

class Post(BaseModel):
    id: Optional[str] = Field(alias="_id")
    title: str
    author_id: str
    content: str
    hashtags: List[str]
    pictures: Optional[List[str]] = []
    videos: Optional[List[str]] = []
    created_at: Optional[str]
    updated_at: Optional[str]
    likes_count: int = 0
    dislikes_count: int = 0
    comments_count: int = 0

class PostCreate(BaseModel):
    title: str
    content: str
    hashtags: List[str]
    pictures: Optional[List[str]] = []
    videos: Optional[List[str]] = []

class PostResponse(BaseModel):
    id: str
    title: str
    author_id: str
    content: str
    hashtags: List[str]
    pictures: Optional[List[str]] = []
    videos: Optional[List[str]] = []
    likes_count: int
    dislikes_count: int
    comments_count: int
    comments: List[Comment]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
