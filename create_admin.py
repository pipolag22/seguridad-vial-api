import os
import sys
from sqlmodel import Session, select
from passlib.context import CryptContext

# Configura el path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import create_db_and_tables, engine
from app.models.user import User, UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin_user():
    print("Iniciando script create_admin.py...")
    create_db_and_tables()
    
    with Session(engine) as session:
        existing_admin = session.exec(select(User).where(User.username == "admin")).first()
        
        if not existing_admin:
            hashed_password = pwd_context.hash("adminpassword123")
            admin_user = User(
                username="admin",
                hashed_password=hashed_password,
                is_active=True,
                role=UserRole.ADMIN,
                dni="12345678",
                nombres="Administrador",
                apellidos="Principal"
            )
            session.add(admin_user)
            session.commit()
            print(f"¡Usuario administrador creado con éxito! ID: {admin_user.id}")
        else:
            print("El usuario 'admin' ya existe")

if __name__ == "__main__":
    create_admin_user()