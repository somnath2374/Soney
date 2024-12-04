from pydantic import BaseModel, Field
from typing import Optional

class HoneytrapCreate(BaseModel):
    purpose: str
    