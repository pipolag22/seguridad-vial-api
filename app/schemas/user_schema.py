from sqlmodel import SQLModel
from enum import Enum

class UserRole(str, Enum):
    NORMAL = "normal"
    INSPECTOR = "inspector"
    JUEZ = "juez"
    ADMIN = "admin"

class UserRead(SQLModel):
    id: int
    username: str
    is_active: bool
    role: UserRole  # Añadido
    dni: str  # Añadido
    nombres: str  # Añadido
    apellidos: str  # Añadido