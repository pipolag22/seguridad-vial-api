from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import date
from enum import Enum

# Importar los modelos relacionados para las relaciones
# Asegúrate de que estos archivos existan en tu estructura (app/models/person.py, app/models/traffic_safety_course.py, etc.)
from app.models.person import Person
from app.models.traffic_safety_course import TrafficSafetyCourse
from app.models.inspector import Inspector
from app.models.judge import Judge


class CourseEnrollmentStatus(str, Enum):
    PENDING = "pending"       # Inscrito, esperando completar el curso
    COMPLETED = "completed"   # Curso completado, válido por un tiempo
    USED = "used"             # Curso usado por un inspector/juez
    EXPIRED = "expired"       # Curso ha caducado (fecha de expiración pasada)
    INCOMPLETE = "incomplete" # Curso no completado a tiempo (pasó la fecha límite, pero no la de expiración total)

class CourseEnrollment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    person_id: int = Field(foreign_key="person.id", index=True) # Añadir index para búsquedas eficientes
    course_id: int = Field(foreign_key="trafficsafetycourse.id", index=True) # Añadir index

    enrollment_date: date = Field(default_factory=date.today) # Fecha de inscripción
    completion_date: Optional[date] = None # Fecha en la que el curso fue completado
    deadline_date: date # Fecha límite para completar el curso (ej. 2 meses desde enrollment_date)
    expiration_date: date # Fecha en que la certificación caduca (ej. 6 meses desde completion_date o fecha de uso)

    status: CourseEnrollmentStatus = Field(default=CourseEnrollmentStatus.PENDING, index=True) # Añadir index

    inspector_id: Optional[int] = Field(default=None, foreign_key="inspector.id", index=True)
    judge_id: Optional[int] = Field(default=None, foreign_key="judge.id", index=True)

    # --- Relaciones ---
    # Una inscripción pertenece a una Persona
    person: Person = Relationship(back_populates="course_enrollments")
    # Una inscripción pertenece a un Curso
    course: TrafficSafetyCourse = Relationship(back_populates="course_enrollments")
    # Una inscripción puede ser usada por un Inspector (Opcional)
    inspector: Optional[Inspector] = Relationship(back_populates="used_enrollments")
    # Una inscripción puede ser usada por un Juez (Opcional)
    judge: Optional[Judge] = Relationship(back_populates="used_enrollments")