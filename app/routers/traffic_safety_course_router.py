from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

# Importa los modelos Pydantic/SQLModel para las entradas y salidas
from app.models import TrafficSafetyCourse, TrafficSafetyCourseCreate, TrafficSafetyCourseRead, TrafficSafetyCourseUpdate
# Importa las funciones de servicio que acabamos de crear
from app.services import traffic_safety_course_service # Asumo que tienes un __init__.py en app/services/ que expone esto
# Si no tienes un __init__.py en services, cambia la línea anterior por:
# from app.services.traffic_safety_course_service import (
#     create_course, get_course_by_id, get_all_courses, update_course, delete_course
# )


from app.config.database import get_session # Para obtener la sesión de la base de datos

# Define el APIRouter
router = APIRouter(
    prefix="/courses",  # Prefijo para todas las rutas en este router (ej. /courses/1)
    tags=["Traffic Safety Courses"], # Etiqueta para la documentación de Swagger/OpenAPI
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=TrafficSafetyCourseRead, status_code=status.HTTP_201_CREATED)
def create_new_course(
    course_create: TrafficSafetyCourseCreate,
    session: Session = Depends(get_session)
):
    """
    Crea un nuevo curso de seguridad vial.
    """
    return traffic_safety_course_service.create_course(course_create, session)

@router.get("/{course_id}", response_model=TrafficSafetyCourseRead)
def read_course(
    course_id: int,
    session: Session = Depends(get_session)
):
    """
    Obtiene un curso de seguridad vial por su ID.
    """
    course = traffic_safety_course_service.get_course_by_id(course_id, session)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.get("/", response_model=List[TrafficSafetyCourseRead])
def read_all_courses(
    session: Session = Depends(get_session)
):
    """
    Obtiene todos los cursos de seguridad vial.
    """
    return traffic_safety_course_service.get_all_courses(session)

@router.put("/{course_id}", response_model=TrafficSafetyCourseRead)
def update_existing_course(
    course_id: int,
    course_update_data: TrafficSafetyCourseUpdate,
    session: Session = Depends(get_session)
):
    """
    Actualiza un curso de seguridad vial existente por su ID.
    """
    updated_course = traffic_safety_course_service.update_course(course_id, course_update_data, session)
    if not updated_course:
        raise HTTPException(status_code=404, detail="Course not found")
    return updated_course

@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_course(
    course_id: int,
    session: Session = Depends(get_session)
):
    """
    Elimina un curso de seguridad vial por su ID.
    """
    deleted = traffic_safety_course_service.delete_course(course_id, session)
    if not deleted:
        raise HTTPException(status_code=404, detail="Course not found")
    return {"message": "Course deleted successfully"} # O un Response con 204 No Content