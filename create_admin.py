import sys
import os

print("Iniciando script create_admin.py...")

# Asegúrate de que el directorio raíz de la aplicación esté en el path de Python
# Esto es crucial para que las importaciones como 'app.config.database' funcionen.
# Si tu script está en la misma carpeta que la carpeta 'app', esto debería funcionar.
script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from app.config.database import get_session, create_db_and_tables
    from app.services import user_service
    from app.schemas.user_schema import UserCreate
    from app.models.user import User, UserRole # Importar User y UserRole directamente del modelo
    from sqlmodel import Session, select

    print("Importaciones exitosas.")

except ImportError as e:
    print(f"Error de importación: {e}")
    print("Asegúrate de que estás ejecutando el script desde la raíz del proyecto (donde está la carpeta 'app').")
    print("También verifica que tus rutas de importación en 'app/...' son correctas.")
    sys.exit(1) # Salir si hay un error de importación

def create_initial_admin_user():
    print("Intentando crear/verificar la base de datos y tablas...")
    try:
        create_db_and_tables()
        print("Base de datos y tablas verificadas/creadas.")
    except Exception as e:
        print(f"Error al crear/verificar la base de datos: {e}")
        sys.exit(1) # Salir si hay un error con la DB

    username = "admin"
    password = "adminpassword123" # ¡CAMBIA ESTA CONTRASEÑA EN PRODUCCIÓN!
    dni = "12345678" # DNI de ejemplo
    nombres = "Administrador"
    apellidos = "Principal"

    print(f"Buscando si el usuario '{username}' ya existe...")

    session = None # Inicializar session fuera del try
    try:
        session = get_session() # Esto devuelve un generador
        db_session = next(session) # Obtener la sesión real del generador

        # Verificar si el usuario ya existe para evitar duplicados
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
        
        # Usar la función create_user del servicio con el rol de ADMIN
        # user_service.create_user ya maneja la sesión
        admin_user = user_service.create_user(admin_user_data, db_session, role=UserRole.ADMIN)
        print(f"¡Usuario administrador '{admin_user.username}' creado con éxito (ID: {admin_user.id}, DNI: {admin_user.dni}, Rol: {admin_user.role})!")
    except Exception as e:
        print(f"Error inesperado al crear el usuario administrador: {e}")
        # Asegurarse de cerrar la sesión en caso de error
        if session:
            try:
                next(session, None) # Intentar cerrar el generador
            except StopIteration:
                pass
    finally:
        # Esto es importante para cerrar la sesión de forma segura
        if session:
            try:
                next(session, None) # Asegurar que el generador se agote
            except StopIteration:
                pass


if __name__ == "__main__":
    create_initial_admin_user()