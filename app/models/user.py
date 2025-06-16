from __future__ import annotations
from enum import Enum
from sqlmodel import SQLModel, Field
from passlib.context import CryptContext
from typing import Optional


# Contexto para el hashing de contraseñas (sin dependencias circulares)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRole(str, Enum):
    NORMAL = "normal"
    INSPECTOR = "inspector"
    JUDGE = "juez"
    ADMIN = "admin"

class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)
    dni: str = Field(unique=True, max_length=20)
    nombres: str
    apellidos: str
    is_active: Optional[bool] = True
    role: UserRole = Field(default=UserRole.NORMAL)

class UserCreate(UserBase):
    password: str  # Contraseña en texto plano para la creación

class UserRead(UserBase):
    id: int

class UserUpdate(SQLModel):
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None
    dni: Optional[str] = None
    nombres: Optional[str] = None
    apellidos: Optional[str] = None

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str