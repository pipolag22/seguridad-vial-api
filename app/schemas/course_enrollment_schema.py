from sqlmodel import SQLModel
from datetime import date
from typing import Optional, List

from app.models.course_enrollment import CourseEnrollmentStatus # Importa tu Enum de estados

# Esquema para crear una inscripción a un curso
class CourseEnrollmentCreate(SQLModel):
    person_id: int
    course_id: int

# Esquema para actualizar el estado de una inscripción
class CourseEnrollmentUpdateStatus(SQLModel):
    status: CourseEnrollmentStatus # Usar el Enum aquí para mayor seguridad y validación
    inspector_id: Optional[int] = None # Opcional, solo si el nuevo estado es 'used'
    judge_id: Optional[int] = None    # Opcional, solo si el nuevo estado es 'used'


class CourseEnrollmentRead(SQLModel):
    id: int
    person_id: int
    course_id: int
    enrollment_date: date
    completion_date: Optional[date] = None # Se mostrará si el curso fue completado
    deadline_date: date
    expiration_date: date
    status: CourseEnrollmentStatus # El estado guardado en DB (miembro del Enum)
    inspector_id: Optional[int] = None
    judge_id: Optional[int] = None
    
    # Campos adicionales para mostrar información relacionada
    person_name: str
    person_dni: str
    course_name: str
    course_description: str

    # Campos calculados
    current_calculated_status: CourseEnrollmentStatus 
    days_until_deadline: int
    days_until_expiration: int