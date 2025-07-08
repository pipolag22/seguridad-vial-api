from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./seguridad_vial.db")
engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    """Importa los modelos localmente para evitar importaciones circulares"""
    # Importa todos los modelos aquí para que SQLModel.metadata los registre
    from app.models.person import Person
    from app.models.traffic_safety_course import TrafficSafetyCourse
    from app.models.inspector import Inspector
    from app.models.judge import Judge
    from app.models.course_enrollment import CourseEnrollment
    from app.models.user import User
    
    SQLModel.metadata.create_all(engine)
