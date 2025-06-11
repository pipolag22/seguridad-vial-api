import sys
import os

print("Iniciando script create_admin.py...")
script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from app.config.database import get_session, create_db_and_tables
    from app.services import user_service
    from app.schemas.user_schema import UserCreate
    from app.models.user import User, UserRole 
    from sqlmodel import Session, select

    print("Importaciones exitosas.")

except ImportError as e:
    print(f"Error de importación: {e}")
    print("Asegúrate de que estás ejecutando el script desde la raíz del proyecto (donde está la carpeta 'app').")
    print("También verifica que tus rutas de importación en 'app/...' son correctas.")
    sys.exit(1) 

def create_initial_admin_user():
    print("Intentando crear/verificar la base de datos y tablas...")
    try:
        create_db_and_tables()
        print("Base de datos y tablas verificadas/creadas.")
    except Exception as e:
        print(f"Error al crear/verificar la base de datos: {e}")
        sys.exit(1) 

    username = "admin"
    password = "adminpassword123" # 
    dni = "12345678" 
    nombres = "Administrador"
    apellidos = "Principal"

    print(f"Buscando si el usuario '{username}' ya existe...")

    session = None 
    try:
        session = get_session() 
        db_session = next(session) 

        existing_user = db_session.exec(select(User).where(User.username == username)).first()
        if existing_user:
            print(f"El usuario '{username}' ya existe. ¡No se creó un nuevo administrador!")
            return

        print(f"El usuario '{username}' no existe. Procediendo a crearlo...")
        admin_user_data = UserCreate(
            username=username,
            password=password,
            dni=dni,
            nombres=nombres,
            apellidos=apellidos
        )
        
        
        admin_user = user_service.create_user(admin_user_data, db_session, role=UserRole.ADMIN)
        print(f"¡Usuario administrador '{admin_user.username}' creado con éxito (ID: {admin_user.id}, DNI: {admin_user.dni}, Rol: {admin_user.role})!")
    except Exception as e:
        print(f"Error inesperado al crear el usuario administrador: {e}")
        
        if session:
            try:
                next(session, None) 
            except StopIteration:
                pass
    finally:
   
        if session:
            try:
                next(session, None) 
            except StopIteration:
                pass


if __name__ == "__main__":
    create_initial_admin_user()