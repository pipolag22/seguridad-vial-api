from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from app.config.database import create_db_and_tables, engine, get_session, Session as DBSession

from app.routers.person_router import router as person_router
from app.routers.traffic_safety_course_router import router as course_router
from app.routers.course_enrollment_router import router as enrollment_router
from app.routers.inspector_router import router as inspector_router
from app.routers.judge_router import router as judge_router
from app.routers.user_router import router as user_router

from importlib.metadata import version as get_package_version
from app.security.security import decode_access_token
from app.services.user_service import get_user_by_username


API_VERSION = "1.0.0"

app = FastAPI(
    title="API de Gestión de Cursos de Seguridad Vial",
    description="API para gestionar personas, cursos, inspectores, jueces e inscripciones de seguridad vial, con transformación de negocio y desnormalización de datos.",
    version=API_VERSION,
)

@app.on_event("startup")
def on_startup():
    """
    Función que se ejecuta al inicio de la aplicación.
    Crea las tablas de la base de datos si no existen.
    """
    create_db_and_tables()

app.include_router(person_router)
app.include_router(course_router)
app.include_router(enrollment_router)
app.include_router(inspector_router)
app.include_router(judge_router)
app.include_router(user_router)

@app.get("/")
def root():
    """
    Endpoint raíz de la API.
    """
    return {"message": "API de cursos de seguridad vial. Visita /docs para la documentación interactiva."}


@app.get("/healthcheck", summary="Verifica la salud del servicio y la conexión a la base de datos")
def healthcheck(session: DBSession = Depends(get_session)):
    """
    Verifica la conexión a la base de datos realizando una simple consulta.
    """
    try:
        with session:
            session.execute(select(1))
        return {"status": "ok", "database_connection": "successful"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database connection failed: {e}")


@app.get("/version", summary="Muestra la versión de la API")
def get_api_version():
    """
    Devuelve la versión actual de la API.
    """
    return {"version": API_VERSION}
