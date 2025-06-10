from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str

class UserRead(BaseModel):
    id: int
    username: str
    is_active: bool
    is_admin: bool

class UserLogin(BaseModel):
    username: str
    password: str