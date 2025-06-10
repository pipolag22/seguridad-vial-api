from fastapi import FastAPI, HTTPException, status
from sqlmodel import select
from app.config.database import create_db_and_tables, engine, Session 
from app.routers.person_router import router as person_router
from app.routers.traffic_safety_course_router import router as course_router
from app.routers.course_enrollment_router import router as enrollment_router
from app.routers.inspector_router import router as inspector_router
from app.routers.judge_router import router as judge_router
from importlib.metadata import version as get_package_version 


API_VERSION = "1.0.0" 

app = FastAPI(
    title="API de Gestión de Cursos de Seguridad Vial",
    description="API para gestionar personas, cursos, inspectores, jueces e inscripciones de seguridad vial, con transformación de negocio y desnormalización de datos.",
    version=API_VERSION,
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(person_router)
app.include_router(course_router)
app.include_router(enrollment_router)
app.include_router(inspector_router)
app.include_router(judge_router)

@app.get("/")
def root():
    return {"message": "API de cursos de seguridad vial. Visita /docs para la documentación interactiva."}


@app.get("/healthcheck", summary="Verifica la salud del servicio y la conexión a la base de datos")
def healthcheck():
    try:
        with Session(engine) as session: 
            session.execute(select(1)) 
        return {"status": "ok", "database_connection": "successful"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database connection failed: {e}")


@app.get("/version", summary="Muestra la versión de la API")
def get_api_version():
    return {"version": API_VERSION}
