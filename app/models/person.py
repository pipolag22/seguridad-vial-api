from __future__ import annotations 

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List 




class Person(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    dni: str 

    #Una persona puede tener muchas inscripciones a cursos
    course_enrollments: List["CourseEnrollment"] = Relationship(back_populates="person")