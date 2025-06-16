from sqlmodel import Session, select
from typing import List, Optional
from datetime import date

from app.models import CourseEnrollment, CourseEnrollmentCreate, CourseEnrollmentRead, CourseEnrollmentUpdate, CourseEnrollmentStatus, Person, TrafficSafetyCourse, Inspector, Judge

def create_enrollment(enrollment_create: CourseEnrollmentCreate, session: Session) -> CourseEnrollment:
    """
    Crea una nueva inscripción de curso de seguridad vial.
    """
    if not enrollment_create.deadline_date:
        enrollment_create.deadline_date = date.today()

    if not enrollment_create.expiration_date:
        enrollment_create.expiration_date = date.today()

    new_enrollment = CourseEnrollment.from_orm(enrollment_create) # Usar from_orm para Pydantic V1
    session.add(new_enrollment)
    session.commit()
    session.refresh(new_enrollment)
    return new_enrollment

def get_enrollment_by_id(enrollment_id: int, session: Session) -> Optional[CourseEnrollment]:
    """
    Obtiene una inscripción a curso de seguridad vial por su ID.
    """
    return session.get(CourseEnrollment, enrollment_id)

def get_all_enrollments(session: Session) -> List[CourseEnrollment]:
    """
    Obtiene todas las inscripciones a cursos de seguridad vial.
    """
    return session.exec(select(CourseEnrollment)).all()

def update_enrollment(enrollment_id: int, enrollment_update_data: CourseEnrollmentUpdate, session: Session) -> Optional[CourseEnrollment]:
    """
    Actualiza una inscripción a curso de seguridad vial existente por su ID.
    """
    enrollment = session.get(CourseEnrollment, enrollment_id)
    if not enrollment:
        return None
    
    # Usar .dict(exclude_unset=True) para Pydantic V1
    for key, value in enrollment_update_data.dict(exclude_unset=True).items():
        setattr(enrollment, key, value)
    
    session.add(enrollment)
    session.commit()
    session.refresh(enrollment)
    return enrollment

def delete_enrollment(enrollment_id: int, session: Session) -> bool:
    """
    Elimina una inscripción a curso de seguridad vial por su ID.
    """
    enrollment = session.get(CourseEnrollment, enrollment_id)
    if not enrollment:
        return False
    session.delete(enrollment)
    session.commit()
    return True

def complete_enrollment(enrollment_id: int, inspector_id: int, session: Session) -> Optional[CourseEnrollment]:
    """
    Marca una inscripción como 'completed' y asigna un inspector.
    """
    enrollment = session.get(CourseEnrollment, enrollment_id)
    if not enrollment or enrollment.status != CourseEnrollmentStatus.PENDING:
        return None
    
    enrollment.status = CourseEnrollmentStatus.COMPLETED
    enrollment.completion_date = date.today()
    enrollment.inspector_id = inspector_id
    
    session.add(enrollment)
    session.commit()
    session.refresh(enrollment)
    return enrollment

def use_enrollment(enrollment_id: int, judge_id: int, session: Session) -> Optional[CourseEnrollment]:
    """
    Marca una inscripción como 'used' y asigna un juez.
    Solo si el estado es 'completed'.
    """
    enrollment = session.get(CourseEnrollment, enrollment_id)
    if not enrollment or enrollment.status != CourseEnrollmentStatus.COMPLETED:
        return None
    
    enrollment.status = CourseEnrollmentStatus.USED
    enrollment.judge_id = judge_id
    
    session.add(enrollment)
    session.commit()
    session.refresh(enrollment)
    return enrollment

def get_enrollments_by_person_id(person_id: int, session: Session) -> List[CourseEnrollment]:
    """
    Obtiene todas las inscripciones de una persona específica.
    """
    return session.exec(select(CourseEnrollment).where(CourseEnrollment.person_id == person_id)).all()

def get_enrollments_by_course_id(course_id: int, session: Session) -> List[CourseEnrollment]:
    """
    Obtiene todas las inscripciones para un curso específico.
    """
    return session.exec(select(CourseEnrollment).where(CourseEnrollment.course_id == course_id)).all()