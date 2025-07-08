# app/services/user_service.py

from sqlmodel import Session, select
from passlib.context import CryptContext
from typing import Optional, List
from datetime import date # Asegúrate de que date esté importado si se usa en otros métodos

from app.models import User, UserRole, UserCreate, UserUpdate

# Contexto para el hashing de contraseñas
# ESTO DEBE SER pbkdf2_sha256. ¡CRÍTICO!
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def create_user(user_create: UserCreate, session: Session) -> User:
    """
    Crea un nuevo usuario en la base de datos.
    Hashea la contraseña antes de guardarla.
    """
    db_user = User(
        username=user_create.username,
        dni=user_create.dni,
        nombres=user_create.nombres,
        apellidos=user_create.apellidos,
        is_active=user_create.is_active,
        role=user_create.role,
        hashed_password=pwd_context.hash(user_create.password)
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

def get_user_by_username(username: str, session: Session) -> Optional[User]:
    """
    Busca un usuario por su nombre de usuario.
    """
    return session.exec(select(User).where(User.username == username)).first()

def authenticate_user(username: str, password: str, session: Session) -> Optional[User]:
    """
    Autentica un usuario verificando su nombre de usuario y contraseña.
    """
    user = get_user_by_username(username, session)
    if not user:
        print(f"DEBUG: Usuario '{username}' no encontrado.") # Depuración
        return None
    
    # --- LÍNEAS DE DEBUGGING CRÍTICAS ---
    print(f"DEBUG (authenticate): Contraseña hasheada desde DB: '{user.hashed_password}'")
    print(f"DEBUG (authenticate): Contraseña en texto plano (NO HASHEADA): '{password}'")
    print(f"DEBUG (authenticate): pwd_context schemes: {pwd_context.schemes()}")
    # --- FIN LÍNEAS DE DEBUGGING ---

    if not pwd_context.verify(password, user.hashed_password):
        print("DEBUG (authenticate): Verificación de contraseña fallida.") # Depuración
        return None
    print("DEBUG (authenticate): Verificación de contraseña exitosa.") # Depuración
    return user

def get_user_by_id(user_id: int, session: Session) -> Optional[User]:
    """
    Obtiene un usuario por su ID.
    """
    return session.get(User, user_id)

def get_users(session: Session) -> List[User]:
    """
    Obtiene todos los usuarios de la base de datos.
    """
    return session.exec(select(User)).all()

def update_user(user_id: int, user_update_data: UserUpdate, session: Session) -> Optional[User]:
    """
    Actualiza un usuario existente por su ID.
    """
    user = session.get(User, user_id)
    if not user:
        return None
    
    update_data = user_update_data.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        if key == "password" and value is not None:
            setattr(user, "hashed_password", pwd_context.hash(value))
        else:
            setattr(user, key, value)
    
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def delete_user(user_id: int, session: Session) -> bool:
    """
    Elimina un usuario por su ID.
    """
    user = session.get(User, user_id)
    if not user:
        return False
    session.delete(user)
    session.commit()
    return True
