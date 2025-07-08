# app/models/course_enrollment.py
from __future__ import annotations

from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import date
from enum import Enum
# from sqlalchemy.orm import Mapped

# Importar los esquemas de lectura para las relaciones anidadas en el esquema CourseEnrollmentRead
from app.models.person import PersonRead
from app.models.traffic_safety_course import TrafficSafetyCourseRead
from app.models.inspector import InspectorRead
from app.models.judge import JudgeRead

class CourseEnrollmentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    USED = "used"
    EXPIRED = "expired"
    INCOMPLETE = "incomplete"

class CourseEnrollmentBase(SQLModel):
    person_id: int
    course_id: int
    enrollment_date: date = Field(default_factory=date.today)
    completion_date: Optional[date] = None
    deadline_date: date
    expiration_date: date
    status: CourseEnrollmentStatus = Field(default=CourseEnrollmentStatus.PENDING)
    inspector_id: Optional[int] = None
    judge_id: Optional[int] = None

class CourseEnrollmentCreate(CourseEnrollmentBase):
    pass

class CourseEnrollmentRead(CourseEnrollmentBase):
    id: int
    person: Optional[PersonRead] = None
    course: Optional[TrafficSafetyCourseRead] = None
    inspector: Optional[InspectorRead] = None
    judge: Optional[JudgeRead] = None

class CourseEnrollmentUpdate(SQLModel):
    completion_date: Optional[date] = None
    status: Optional[CourseEnrollmentStatus] = None
    inspector_id: Optional[int] = None
    judge_id: Optional[int] = None
    deadline_date: Optional[date] = None
    expiration_date: Optional[date] = None

class CourseEnrollment(CourseEnrollmentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # RELACIONES TEMPORALMENTE ELIMINADAS
    # person: Mapped["Person"] = Relationship(back_populates="course_enrollments")
    # course: Mapped["TrafficSafetyCourse"] = Relationship(back_populates="course_enrollments")
    # inspector: Mapped[Optional["Inspector"]] = Relationship(back_populates="used_enrollments")
    # judge: Mapped[Optional["Judge"]] = Relationship(back_populates="used_enrollments")
