from pydantic import BaseModel
from typing import Optional

class Book(BaseModel):
    title: str
    author: str
    description: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"
