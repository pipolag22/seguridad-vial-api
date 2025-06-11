from sqlmodel import SQLModel, Field, String
from enum import Enum

class UserRole(str, Enum):
    NORMAL = "normal"
    INSPECTOR = "inspector"
    JUEZ = "juez"
    ADMIN = "admin"

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    role: UserRole = Field(default=UserRole.NORMAL)
    dni: str = Field(index=True)
    nombres: str
    apellidos: str