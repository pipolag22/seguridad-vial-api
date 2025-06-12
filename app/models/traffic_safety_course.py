from __future__ import annotations

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List 




class TrafficSafetyCourse(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str

    #Un curso puede tener muchas inscripciones
    course_enrollments: List["CourseEnrollment"] = Relationship(back_populates="course")