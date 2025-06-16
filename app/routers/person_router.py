# app/routers/person_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from pydantic import parse_obj_as # Importar para compatibilidad con Pydantic V1

from app.config.database import get_session
from app.models import Person, PersonCreate, PersonRead, PersonUpdate, User

from app.services import person_service
from app.routers.user_router import get_current_user, get_current_admin_user

router = APIRouter(prefix="/persons", tags=["Persons"])

@router.post("/", response_model=PersonRead, status_code=status.HTTP_201_CREATED)
def create_person(
    person_create: PersonCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Crea una nueva persona.
    Requiere rol de Administrador.
    """
    try:
        new_person = person_service.create_person(person_create, session)
        return new_person
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=List[PersonRead])
def read_all_persons(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene una lista de todas las personas.
    Requiere autenticación.
    """
    return person_service.get_all_persons(session)

@router.get("/{person_id}", response_model=PersonRead)
def read_person(
    person_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene una persona por su ID.
    Requiere autenticación.
    """
    person = person_service.get_person_by_id(person_id, session)
    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")
    return person

@router.put("/{person_id}", response_model=PersonRead)
def update_person(
    person_id: int,
    updated_data: PersonUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Actualiza una persona existente por su ID.
    Requiere rol de Administrador.
    """
    person = person_service.update_person(person_id, updated_data, session)
    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")
    return person

@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_person(
    person_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Elimina una persona por su ID.
    Requiere rol de Administrador.
    """
    if not person_service.delete_person(person_id, session):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")
    return


# ==============================================================================
# Archivo: app/routers/traffic_safety_course_router.py
# Ubicación: app/routers/traffic_safety_course_router.py
# ==============================================================================
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from pydantic import parse_obj_as # Necesario si se usa en esquemas de respuesta


from app.config.database import get_session
# Importar modelos y esquemas necesarios
from app.models import TrafficSafetyCourse, TrafficSafetyCourseCreate, TrafficSafetyCourseRead, TrafficSafetyCourseUpdate, User

# Importar el servicio de cursos
from app.services import traffic_safety_course_service

# Importar dependencias de autenticación y autorización desde el router de usuarios
from app.routers.user_router import get_current_user, get_current_admin_user


router = APIRouter(prefix="/courses", tags=["Courses"])

# --- Endpoint para crear un nuevo curso (solo ADMIN) ---
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

# --- Endpoint para leer todos los cursos (cualquier usuario autenticado) ---
@router.get("/", response_model=List[TrafficSafetyCourseRead])
def read_all_courses(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user) # Cualquier usuario autenticado puede leer
):
    """
    Obtiene una lista de todos los cursos de seguridad vial.
    Requiere autenticación.
    """
    return traffic_safety_course_service.get_all_courses(session)

# --- Endpoint para leer un curso por ID (cualquier usuario autenticado) ---
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

# --- Endpoint para actualizar un curso (solo ADMIN) ---
@router.put("/{course_id}", response_model=TrafficSafetyCourseRead)
def update_course(
    course_id: int,
    updated_data: TrafficSafetyCourseUpdate, # Usar el esquema de actualización
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user) # Solo ADMIN puede modificar cursos
):
    """
    Actualiza un curso de seguridad vial existente por su ID.
    Requiere rol de Administrador.
    """
    course = traffic_safety_course_service.update_course(course_id, updated_data, session)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course

# --- Endpoint para eliminar un curso (solo ADMIN) ---
@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user) # Solo ADMIN puede eliminar cursos
):
    """
    Elimina un curso de seguridad vial por su ID.
    Requiere rol de Administrador.
    """
    if not traffic_safety_course_service.delete_course(course_id, session):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return # Retorna 204 No Content, no necesita cuerpo de respuesta
