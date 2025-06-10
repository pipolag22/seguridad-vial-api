from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError  
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserRead, UserLogin
from app.security.security import get_password_hash, verify_password, create_access_token
from fastapi import HTTPException, status
from datetime import timedelta 
from typing import Optional

ACCESS_TOKEN_EXPIRE_MINUTES = 120

def create_user(user_data: UserCreate, session: Session) -> UserRead:
    """Crea un nuevo usuario en la base de datos."""
    hashed_password = get_password_hash(user_data.password)
    db_user = User(username=user_data.username, hashed_password=hashed_password)
    
    session.add(db_user)
    try:
        session.commit()
        session.refresh(db_user)
        return UserRead(
    id=db_user.id,
    username=db_user.username,
    is_active=db_user.is_active,
    is_admin=db_user.is_admin
)
    except IntegrityError:  
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está en uso. Por favor, elige otro."
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear el usuario: {str(e)}"
        )


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
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return access_token

def get_user_by_username(username: str, session: Session) -> Optional[UserRead]:
    """Obtiene un usuario por su nombre de usuario."""
    user = session.exec(select(User).where(User.username == username)).first()
    if user:
        return UserRead(
    id=user.id,
    username=user.username,
    is_active=user.is_active,
    is_admin=user.is_admin
)
    return None