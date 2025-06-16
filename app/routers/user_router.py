# app/routers/user_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlmodel import Session, select
from typing import List

from app.config.database import get_session
from app.models import User, UserRole, UserCreate, UserRead, UserUpdate

from app.security import security
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    """
    Dependencia para obtener el usuario actual autenticado.
    Verifica el token de acceso.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = security.decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    user = user_service.get_user_by_username(username, session)
    if user is None:
        raise credentials_exception
    return user

def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependencia para obtener el usuario actual que es ADMIN.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not an admin user")
    return current_user

def get_current_inspector_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependencia para obtener el usuario actual que es INSPECTOR.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.INSPECTOR]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not an inspector or admin user")
    return current_user

def get_current_judge_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependencia para obtener el usuario actual que es JUEZ.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.JUEZ]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a judge or admin user")
    return current_user

@router.post("/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    """
    Endpoint para que los usuarios obtengan un token de acceso OAuth2.
    """
    user = user_service.authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = security.timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username, "role": user.role.value}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(
    user_create: UserCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user) # Solo ADMIN puede crear usuarios
):
    """
    Crea un nuevo usuario (solo para administradores).
    """
    existing_user = user_service.get_user_by_username(user_create.username, session)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    
    new_user = user_service.create_user(user_create, session)
    return new_user

@router.get("/", response_model=List[UserRead])
def read_users(session: Session = Depends(get_session), current_user: User = Depends(get_current_admin_user)):
    """
    Obtiene todos los usuarios (solo para administradores).
    """
    return user_service.get_users(session)

@router.get("/{user_id}", response_model=UserRead)
def read_user(user_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """
    Obtiene un usuario por ID. Los usuarios normales solo pueden verse a sí mismos.
    Los administradores pueden ver cualquier usuario.
    """
    user = user_service.get_user_by_id(user_id, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this user")
    return user

@router.put("/{user_id}", response_model=UserRead)
def update_user_endpoint(
    user_id: int,
    user_update: UserUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza un usuario por ID. Los usuarios normales solo pueden actualizar su propia información.
    Los administradores pueden actualizar cualquier usuario.
    """
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user")

    user_data = user_update.dict(exclude_unset=True) # Usar .dict() para Pydantic V1
    updated_user = user_service.update_user(user_id, user_data, session)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_endpoint(user_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_admin_user)):
    """
    Elimina un usuario por ID (solo para administradores).
    """
    if not user_service.delete_user(user_id, session):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return
