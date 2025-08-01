# app/services/traffic_safety_course_service.py

from sqlmodel import Session, select
from typing import List, Optional


from app.models import TrafficSafetyCourse, TrafficSafetyCourseCreate, TrafficSafetyCourseRead, TrafficSafetyCourseUpdate

def create_course(course_create: TrafficSafetyCourseCreate, session: Session) -> TrafficSafetyCourse:
    """
    Crea un nuevo curso de seguridad vial en la base de datos.
    """
    new_course = TrafficSafetyCourse.model_validate(course_create) 
    session.add(new_course)
    session.commit()
    session.refresh(new_course)
    return new_course

def get_course_by_id(course_id: int, session: Session) -> Optional[TrafficSafetyCourse]:
    """
    Obtiene un curso de seguridad vial por su ID.
    """
    return session.get(TrafficSafetyCourse, course_id)

def get_all_courses(session: Session) -> List[TrafficSafetyCourse]:
    """
    Obtiene todos los cursos de seguridad vial de la base de datos.
    """
    return session.exec(select(TrafficSafetyCourse)).all()

def update_course(course_id: int, course_update_data: TrafficSafetyCourseUpdate, session: Session) -> Optional[TrafficSafetyCourse]:
    """
    Actualiza un curso de seguridad vial existente por su ID.
    """
    course = session.get(TrafficSafetyCourse, course_id)
    if not course:
        return None
    
    # Actualiza los campos del modelo con los datos de entrada
    # Usar model_dump(exclude_unset=True) para Pydantic V2
    course_data = course_update_data.model_dump(exclude_unset=True)
    for key, value in course_data.items():
        setattr(course, key, value)
    
    session.add(course)
    session.commit()
    session.refresh(course)
    return course

def delete_course(course_id: int, session: Session) -> bool:
    """
    Elimina un curso de seguridad vial por su ID.
    """
    course = session.get(TrafficSafetyCourse, course_id)
    if not course:
        return False
    session.delete(course)
    session.commit()
    return True