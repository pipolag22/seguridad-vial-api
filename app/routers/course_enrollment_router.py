# app/routers/course_enrollment_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, col, and_
from typing import List, Optional
from sqlalchemy.orm import selectinload # Importar selectinload para cargar relaciones
from pydantic import parse_obj_as # Importar para compatibilidad con Pydantic V1

from app.config.database import get_session
from app.models import CourseEnrollment, CourseEnrollmentCreate, CourseEnrollmentRead, CourseEnrollmentUpdate, User, CourseEnrollmentStatus, Person, TrafficSafetyCourse, Inspector, Judge

from app.services import course_enrollment_service
from app.routers.user_router import get_current_user, get_current_admin_user, get_current_inspector_user, get_current_judge_user

router = APIRouter(prefix="/enrollments", tags=["Course Enrollments"])

@router.post("/", response_model=CourseEnrollmentRead, status_code=status.HTTP_201_CREATED)
def create_enrollment(
    enrollment_create: CourseEnrollmentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user) # Solo ADMIN puede crear
):
    """
    Crea una nueva inscripción de curso de seguridad vial.
    Requiere rol de Administrador.
    """
    try:
        new_enrollment = course_enrollment_service.create_enrollment(enrollment_create, session)
        return new_enrollment
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=List[CourseEnrollmentRead])
def read_all_enrollments(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user) # Cualquier user autenticado puede leer
):
    """
    Obtiene una lista de todas las inscripciones a cursos de seguridad vial.
    Requiere autenticación.
    """
    # Usar `options(selectinload(...))` para cargar relaciones si se necesitan en CourseEnrollmentRead
    # Esta es una buena práctica para evitar N+1 queries.
    enrollments = session.exec(
        select(CourseEnrollment)
        .options(selectinload(CourseEnrollment.person))
        .options(selectinload(CourseEnrollment.course))
        .options(selectinload(CourseEnrollment.inspector))
        .options(selectinload(CourseEnrollment.judge))
    ).all()
    # Convertir los objetos SQLModel (ORM) a los esquemas de lectura de Pydantic
    # parse_obj_as es la forma de Pydantic V1 de hacer lo que model_validate hace en V2.
    return parse_obj_as(List[CourseEnrollmentRead], enrollments)

@router.get("/{enrollment_id}", response_model=CourseEnrollmentRead)
def read_enrollment(
    enrollment_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene una inscripción a curso de seguridad vial por su ID.
    Requiere autenticación.
    """
    enrollment = session.exec(
        select(CourseEnrollment)
        .where(CourseEnrollment.id == enrollment_id)
        .options(selectinload(CourseEnrollment.person))
        .options(selectinload(CourseEnrollment.course))
        .options(selectinload(CourseEnrollment.inspector))
        .options(selectinload(CourseEnrollment.judge))
    ).first()
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
    return parse_obj_as(CourseEnrollmentRead, enrollment)

@router.put("/{enrollment_id}", response_model=CourseEnrollmentRead)
def update_enrollment(
    enrollment_id: int,
    updated_data: CourseEnrollmentUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user) # Solo ADMIN puede actualizar
):
    """
    Actualiza una inscripción a curso de seguridad vial existente por su ID.
    Requiere rol de Administrador.
    """
    enrollment = course_enrollment_service.update_enrollment(enrollment_id, updated_data, session)
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
    
    # Después de actualizar, cargar las relaciones para la respuesta
    updated_enrollment_with_relations = session.exec(
        select(CourseEnrollment)
        .where(CourseEnrollment.id == enrollment.id)
        .options(selectinload(CourseEnrollment.person))
        .options(selectinload(CourseEnrollment.course))
        .options(selectinload(CourseEnrollment.inspector))
        .options(selectinload(CourseEnrollment.judge))
    ).first()
    return parse_obj_as(CourseEnrollmentRead, updated_enrollment_with_relations)


@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_enrollment(
    enrollment_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user) # Solo ADMIN puede eliminar
):
    """
    Elimina una inscripción a curso de seguridad vial por su ID.
    Requiere rol de Administrador.
    """
    if not course_enrollment_service.delete_enrollment(enrollment_id, session):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
    return

# --- Endpoints específicos para inspectores y jueces ---

@router.post("/{enrollment_id}/complete", response_model=CourseEnrollmentRead)
def complete_enrollment(
    enrollment_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_inspector_user) # Solo Inspector puede marcar como completado
):
    """
    Marca una inscripción como 'completed'.
    Requiere rol de Inspector.
    """
    enrollment = course_enrollment_service.complete_enrollment(enrollment_id, current_user.id, session)
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found or already completed")
    
    # Cargar relaciones para la respuesta
    completed_enrollment_with_relations = session.exec(
        select(CourseEnrollment)
        .where(CourseEnrollment.id == enrollment.id)
        .options(selectinload(CourseEnrollment.person))
        .options(selectinload(CourseEnrollment.course))
        .options(selectinload(CourseEnrollment.inspector))
        .options(selectinload(CourseEnrollment.judge))
    ).first()
    return parse_obj_as(CourseEnrollmentRead, completed_enrollment_with_relations)


@router.post("/{enrollment_id}/use", response_model=CourseEnrollmentRead)
def use_enrollment(
    enrollment_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_judge_user) # Solo Juez puede marcar como usado
):
    """
    Marca una inscripción como 'used'.
    Requiere rol de Juez.
    """
    enrollment = course_enrollment_service.use_enrollment(enrollment_id, current_user.id, session)
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found or not in a 'completed' state")
    
    # Cargar relaciones para la respuesta
    used_enrollment_with_relations = session.exec(
        select(CourseEnrollment)
        .where(CourseEnrollment.id == enrollment.id)
        .options(selectinload(CourseEnrollment.person))
        .options(selectinload(CourseEnrollment.course))
        .options(selectinload(CourseEnrollment.inspector))
        .options(selectinload(CourseEnrollment.judge))
    ).first()
    return parse_obj_as(CourseEnrollmentRead, used_enrollment_with_relations)


@router.get("/person/{person_id}", response_model=List[CourseEnrollmentRead])
def get_enrollments_by_person(
    person_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene todas las inscripciones de una persona específica.
    """
    enrollments = session.exec(
        select(CourseEnrollment)
        .where(CourseEnrollment.person_id == person_id)
        .options(selectinload(CourseEnrollment.person))
        .options(selectinload(CourseEnrollment.course))
        .options(selectinload(CourseEnrollment.inspector))
        .options(selectinload(CourseEnrollment.judge))
    ).all()
    return parse_obj_as(List[CourseEnrollmentRead], enrollments)

@router.get("/course/{course_id}", response_model=List[CourseEnrollmentRead])
def get_enrollments_by_course(
    course_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene todas las inscripciones para un curso específico.
    """
    enrollments = session.exec(
        select(CourseEnrollment)
        .where(CourseEnrollment.course_id == course_id)
        .options(selectinload(CourseEnrollment.person))
        .options(selectinload(CourseEnrollment.course))
        .options(selectinload(CourseEnrollment.inspector))
        .options(selectinload(CourseEnrollment.judge))
    ).all()
    return parse_obj_as(List[CourseEnrollmentRead], enrollments)

@router.get("/status/{status_value}", response_model=List[CourseEnrollmentRead])
def get_enrollments_by_status(
    status_value: CourseEnrollmentStatus,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene todas las inscripciones con un estado específico.
    """
    enrollments = session.exec(
        select(CourseEnrollment)
        .where(CourseEnrollment.status == status_value)
        .options(selectinload(CourseEnrollment.person))
        .options(selectinload(CourseEnrollment.course))
        .options(selectinload(CourseEnrollment.inspector))
        .options(selectinload(CourseEnrollment.judge))
    ).all()
    return parse_obj_as(List[CourseEnrollmentRead], enrollments)
