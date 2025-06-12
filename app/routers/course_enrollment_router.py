from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.config.database import get_session
from app.schemas.course_enrollment_schema import CourseEnrollmentCreate, CourseEnrollmentRead, CourseEnrollmentUpdateStatus
from app.services import course_enrollment_service
from typing import List, Optional


from app.models.user import User, UserRole 
from app.models.person import Person 

from app.routers.user_router import get_current_user, get_current_admin_user


def get_current_inspector_or_juez_user(current_user: User = Depends(get_current_user)):
    """Dependencia para verificar si el usuario actual es inspector o juez."""
    if current_user.role not in [UserRole.INSPECTOR, UserRole.JUEZ, UserRole.ADMIN]: # También admin puede buscar
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient privileges. Requires Inspector, Judge or Admin role.",
        )
    return current_user

router = APIRouter(prefix="/enrollments", tags=["Course Enrollments"])

@router.post("/", response_model=CourseEnrollmentRead, status_code=status.HTTP_201_CREATED)
def create_enrollment(
    enrollment_data: CourseEnrollmentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user) # Solo ADMIN puede crear inscripciones
):
    """Crea una nueva inscripción a un curso (solo para administradores)."""
    return course_enrollment_service.create_enrollment(enrollment_data, session)


@router.get("/", response_model=List[CourseEnrollmentRead])
def read_all_enrollments(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user) # Solo ADMIN puede ver todas las inscripciones
):
    """Obtiene todas las inscripciones (solo para administradores)."""
    return course_enrollment_service.get_all_enrollments(session)

@router.get("/{enrollment_id}", response_model=CourseEnrollmentRead)
def read_enrollment(
    enrollment_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user) # Cualquier usuario autenticado puede acceder
):
    """Obtiene una inscripción por su ID. Restringe acceso según el rol."""
    enrollment = course_enrollment_service.get_enrollment_by_id(enrollment_id, session)
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course Enrollment not found")
    
   
    # Un usuario normal solo puede ver sus propias inscripciones.
    # Administradores, inspectores y jueces pueden ver cualquier inscripción.
    if current_user.role == UserRole.NORMAL:
        if not enrollment.person or current_user.dni != enrollment.person.dni:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only view your own enrollments.")
    
    return enrollment

@router.get("/by_dni/{person_dni}", response_model=List[CourseEnrollmentRead])
def read_enrollments_by_dni(
    person_dni: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_inspector_or_juez_user) # Solo ADMIN, INSPECTOR, JUEZ pueden buscar por DNI
):
    """Obtiene inscripciones de una persona por su DNI (solo para administradores, inspectores, jueces)."""
    enrollments = course_enrollment_service.get_enrollments_by_person_dni(person_dni, session)
    if not enrollments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No enrollments found for DNI: {person_dni}")
    return enrollments


@router.put("/{enrollment_id}/status", response_model=CourseEnrollmentRead)
def update_enrollment_status_api(
    enrollment_id: int,
    status_update: CourseEnrollmentUpdateStatus, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user) # Cualquier usuario autenticado puede intentar cambiar el estado
):
    """
    Actualiza el estado de una inscripción.
    La autorización se maneja en la capa de servicio según el rol del usuario y el estado.
    """
    return course_enrollment_service.update_enrollment_status(
        enrollment_id, status_update, session, current_user # Pasa el usuario actual al servicio
    )


@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_enrollment(
    enrollment_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user) 
):
    """Elimina una inscripción (solo para administradores)."""
    if not course_enrollment_service.delete_enrollment(enrollment_id, session):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course Enrollment not found")
    return # No devuelve contenido para 204 (HTTP 204 No Content)