from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from app.config.database import get_session
from app.schemas.user_schema import UserCreate, UserRead
from app.services import user_service
from typing import Annotated

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=UserRead)
def register_user(user_data: UserCreate, session: Session = Depends(get_session)):
    """Registra un nuevo usuario normal."""
    db_user = user_service.get_user_by_username(user_data.username, session)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return user_service.create_user(user_data, session)

@router.post("/create_inspector", response_model=UserRead)
def create_inspector(user_data: UserCreate, session: Session = Depends(get_session), current_user: UserRead = Depends(get_current_user)):
    """Crea un nuevo inspector (solo para administradores)."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
    return user_service.create_inspector(user_data, session)

@router.post("/create_juez", response_model=UserRead)
def create_juez(user_data: UserCreate, session: Session = Depends(get_session), current_user: UserRead = Depends(get_current_user)):
    """Crea un nuevo juez (solo para administradores)."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
    return user_service.create_juez(user_data, session)

@router.post("/token")
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Session = Depends(get_session)
):
    user = user_service.authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = user_service.create_user_access_token(user)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserRead)
def read_users_me(current_user: UserRead = Depends(get_current_user)):
    """Obtiene la información del usuario actual."""
    return current_user


def get_current_user(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)
) -> UserRead:
    from app.security.security import decode_access_token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = user_service.get_user_by_username(username, session)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_admin_user(current_user: UserRead = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient privileges",
        )
    return current_user