from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm 
from sqlmodel import Session
from app.config.database import get_session
from app.schemas.user_schema import UserCreate, UserRead, UserLogin
from app.services import user_service 
from app.security.security import decode_access_token 

router = APIRouter(prefix="/users", tags=["Users"])


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token") 

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, session: Session = Depends(get_session)):
    """Registra un nuevo usuario."""
    db_user = user_service.get_user_by_username(user_data.username, session)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nombre de usuario ya registrado")
    
    user = user_service.create_user(user_data, session)
    return user

@router.post("/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    session: Session = Depends(get_session)
):
    """Inicia sesión y obtiene un token de acceso."""
    user = user_service.authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = user_service.create_user_access_token(user)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
def read_users_me(
    token: str = Depends(oauth2_scheme), 
    session: Session = Depends(get_session)
):
    """Obtiene la información del usuario autenticado."""
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado")
    
    username: str = payload.get("sub") 
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token malformado")
    
    user = user_service.get_user_by_username(username, session)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")
    
    return user