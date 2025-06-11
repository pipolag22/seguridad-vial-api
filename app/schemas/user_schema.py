from sqlmodel import SQLModel 
from pydantic import Field
from enum import Enum 

class UserRole(str, Enum):
    NORMAL = "normal"
    INSPECTOR = "inspector"
    JUEZ = "juez"
    ADMIN = "admin"

class UserCreate(SQLModel): # 
    username: str
    password: str
    dni: str
    nombres: str
    apellidos: str

class UserLogin(SQLModel): 
    username: str
    password: str

class UserRead(SQLModel): 
    id: int
    username: str
    is_active: bool
    role: UserRole
    dni: str
    nombres: str
    apellidos: str