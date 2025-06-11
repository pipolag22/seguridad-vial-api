from sqlmodel import Session, select
from app.models.user import User, UserRole
from app.schemas.user_schema import UserCreate, UserRead
from app.security.security import get_password_hash, create_access_token
from fastapi import HTTPException, status
from datetime import timedelta
from typing import Optional

ACCESS_TOKEN_EXPIRE_MINUTES = 120

def create_user(user_data: UserCreate, session: Session, role: UserRole = UserRole.NORMAL) -> UserRead:
    """Crea un nuevo usuario en la base de datos."""
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        hashed_password=hashed_password,
        dni=user_data.dni,
        nombres=user_data.nombres,
        apellidos=user_data.apellidos,
        role=role  
    )
    session.add(db_user)
    try:
        session.commit()
        session.refresh(db_user)
        return UserRead.model_validate(db_user)
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error creando usuario: {e}")

def create_inspector(user_data: UserCreate, session: Session) -> UserRead:
    """Crea un nuevo inspector (solo para administradores)."""
    return create_user(user_data, session, role=UserRole.INSPECTOR)

def create_juez(user_data: UserCreate, session: Session) -> UserRead:
    """Crea un nuevo juez (solo para administradores)."""
    return create_user(user_data, session, role=UserRole.JUEZ)

def get_user_by_username(username: str, session: Session) -> Optional[UserRead]:
    """Obtiene un usuario por su nombre de usuario."""
    user = session.exec(select(User).where(User.username == username)).first()
    if user:
        return UserRead.model_validate(user)
    return None

def get_user_by_dni(dni: str, session: Session) -> Optional[UserRead]:
    """Obtiene un usuario por su DNI."""
    user = session.exec(select(User).where(User.dni == dni)).first()
    if user:
        return UserRead.model_validate(user)
    return None

def authenticate_user(username: str, password: str, session: Session) -> Optional[User]:
    """Autentica un usuario por nombre de usuario y contraseña."""
    user = session.exec(select(User).where(User.username == username)).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_user_access_token(user: User) -> str:
    """Crea un token de acceso para un usuario."""
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, 
        expires_delta=access_token_expires,
    )
    return access_token