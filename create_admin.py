import os
import sys
from sqlmodel import Session, select

# Asegúrate de que el path de la aplicación esté en sys.path para poder importar
# Esto es útil si ejecutas el script desde la raíz del proyecto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from app.config.database import create_db_and_tables, engine, get_session

# Importa User y UserRole desde el paquete 'app.models'
from app.models import User, UserRole
# Importa CryptContext para el hashing de contraseñas
from passlib.context import CryptContext

# Configuración del contexto de contraseñas
# DEBE USAR pbkdf2_sha256
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def create_admin_user():
    """
    Crea un usuario administrador si no existe.
    """
    print("Iniciando script create_admin.py...")
    print("Importaciones exitosas.")

    print("Intentando crear/verificar la base de datos y tablas...")
    create_db_and_tables()
    print("Base de datos y tablas verificadas/creadas.")

    with Session(engine) as session:
        print("Buscando si el usuario 'admin' ya existe...")
        existing_admin = session.exec(select(User).where(User.username == "admin")).first()

        if not existing_admin:
            print("El usuario 'admin' no existe. Procediendo a crearlo...")
            try:
                # Hashear la contraseña del admin con el nuevo algoritmo.
                hashed_password = pwd_context.hash("adminpassword123")

                admin_user = User(
                    username="admin",
                    hashed_password=hashed_password,
                    is_active=True,
                    role=UserRole.ADMIN, # Usar el Enum importado
                    dni="12345678", # Un DNI de ejemplo
                    nombres="Administrador",
                    apellidos="Principal"
                )
                session.add(admin_user)
                session.commit()
                session.refresh(admin_user)
                print(f"¡Usuario administrador '{admin_user.username}' creado con éxito (ID: {admin_user.id}, DNI: {admin_user.dni}, Rol: {admin_user.role})!")
            except Exception as e:
                print(f"Error inesperado al crear el usuario administrador: {e}")
                session.rollback()
        else:
            print("El usuario 'admin' ya existe.")

if __name__ == "__main__":
    create_admin_user()
