from __future__ import annotations
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.orm import relationship as sa_relationship


class TrafficSafetyCourseBase(SQLModel):
    name: str = Field(..., max_length=100, index=True, description="Nombre oficial del curso de seguridad vial")
    description: str = Field(..., max_length=500, description="Descripción detallada del contenido del curso")

class TrafficSafetyCourseCreate(TrafficSafetyCourseBase):
    pass

class TrafficSafetyCourseRead(TrafficSafetyCourseBase):
    id: int

class TrafficSafetyCourseUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=100, description="Nombre oficial del curso de seguridad vial")
    description: Optional[str] = Field(default=None, max_length=500, description="Descripción detallada del contenido del curso")

class TrafficSafetyCourse(TrafficSafetyCourseBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, description="ID único del curso")
    
    course_enrollments: List["CourseEnrollment"] = Relationship(
        back_populates="course",
        sa_relationship=sa_relationship("CourseEnrollment", back_populates="course")
    )