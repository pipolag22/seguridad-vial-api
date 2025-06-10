from sqlmodel import SQLModel
from datetime import date
from typing import Optional

# Esquema base 
class CourseEnrollmentBase(SQLModel):
    person_id: int
    course_id: int
    enrollment_date: date
    deadline_date: date
    expiration_date: date
    status: str
    inspector_id: Optional[int] = None
    judge_id: Optional[int] = None

# nueva inscripción
class CourseEnrollmentCreate(SQLModel):
    person_id: int
    course_id: int
    

# respuesta de la API
class CourseEnrollmentRead(SQLModel):
    id: int
    person_id: int
    course_id: int
    enrollment_date: date
    deadline_date: date
    expiration_date: date
    status: str
    inspector_id: Optional[int] = None
    judge_id: Optional[int] = None

    
    person_name: str
    person_dni: str
    course_name: str
    course_description: str

   
    current_calculated_status: str 
    days_until_deadline: int
    days_until_expiration: int


class CourseEnrollmentUpdateStatus(SQLModel):
    status: str
    inspector_id: Optional[int] = None
    judge_id: Optional[int] = None