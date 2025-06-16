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
    SQLModel.metadata.create_all(engine)