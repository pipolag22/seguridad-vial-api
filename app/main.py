from fastapi import FastAPI
from app.config.database import create_db_and_tables
from app.routers.person_router import router as person_router
from app.routers.traffic_safety_course_router import router as course_router
from app.routers.course_enrollment_router import router as enrollment_router
from app.routers.inspector_router import router as inspector_router
from app.routers.judge_router import router as judge_router


app = FastAPI()

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
    return {"message": "API de cursos de seguridad vial"}