# app/routers/traffic_safety_course_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from pydantic import parse_obj_as # Importar para compatibilidad con Pydantic V1

from app.config.database import get_session
from app.models import TrafficSafetyCourse, TrafficSafetyCourseCreate, TrafficSafetyCourseRead, TrafficSafetyCourseUpdate, User

from app.services import traffic_safety_course_service
from app.routers.user_router import get_current_admin_user, get_current_user # Importar get_current_user también

router = APIRouter(prefix="/courses", tags=["Traffic Safety Courses"])

@router.post("/", response_model=TrafficSafetyCourseRead, status_code=status.HTTP_201_CREATED)
def create_course(
    course_create: TrafficSafetyCourseCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user) # Solo ADMIN puede crear cursos
):
    """
    Crea un nuevo curso de seguridad vial.
    Requiere rol de Administrador.
    """
    try:
        new_course = traffic_safety_course_service.create_course(course_create, session)
        return new_course
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=List[TrafficSafetyCourseRead])
def read_all_courses(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user) # Cualquier usuario autenticado puede leer
):
    """
    Obtiene una lista de todos los cursos de seguridad vial.
    Requiere autenticación.
    """
    courses = traffic_safety_course_service.get_all_courses(session)
    # Convertir los objetos SQLModel (ORM) a los esquemas de lectura de Pydantic
    return parse_obj_as(List[TrafficSafetyCourseRead], courses)

@router.get("/{course_id}", response_model=TrafficSafetyCourseRead)
def read_course(
    course_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user) # Cualquier usuario autenticado puede leer
):
    """
    Obtiene un curso de seguridad vial por su ID.
    Requiere autenticación.
    """
    course = traffic_safety_course_service.get_course_by_id(course_id, session)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course

@router.put("/{course_id}", response_model=TrafficSafetyCourseRead)
def update_course(
    course_id: int,
    course_update: TrafficSafetyCourseUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user) # Solo ADMIN puede actualizar
):
    """
    Actualiza un curso de seguridad vial existente por su ID.
    Requiere rol de Administrador.
    """
    updated_course = traffic_safety_course_service.update_course(course_id, course_update, session)
    if not updated_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return updated_course

@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user) # Solo ADMIN puede eliminar
):
    """
    Elimina un curso de seguridad vial por su ID.
    Requiere rol de Administrador.
    """
    if not traffic_safety_course_service.delete_course(course_id, session):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return
