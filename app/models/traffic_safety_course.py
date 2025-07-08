# app/models/traffic_safety_course.py
from __future__ import annotations

from sqlmodel import SQLModel, Field
from typing import Optional, List
# from sqlalchemy.orm import Mapped

class TrafficSafetyCourseBase(SQLModel):
    name: str
    description: str

class TrafficSafetyCourseCreate(TrafficSafetyCourseBase):
    pass

class TrafficSafetyCourseRead(TrafficSafetyCourseBase):
    id: int

class TrafficSafetyCourseUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None

class TrafficSafetyCourse(TrafficSafetyCourseBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # RELACIÓN TEMPORALMENTE ELIMINADA
    # course_enrollments: Mapped[List["CourseEnrollment"]] = Relationship(back_populates="course")
