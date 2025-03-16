from pydantic import BaseModel
from typing import Optional

# User schema for registration
class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"

# Schema for token response
class Token(BaseModel):
    access_token: str
    token_type: str

# Book schema
class Book(BaseModel):
    title: str
    author: str
    description: Optional[str] = None
