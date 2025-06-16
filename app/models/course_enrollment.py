from __future__ import annotations
from typing import Optional
from datetime import date
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.orm import relationship as sa_relationship


class CourseEnrollmentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    USED = "used"
    EXPIRED = "expired"
    INCOMPLETE = "incomplete"

class CourseEnrollmentBase(SQLModel):
    person_id: int = Field(foreign_key="person.id")
    course_id: int = Field(foreign_key="trafficsafetycourse.id")
    enrollment_date: date = Field(default_factory=date.today)
    completion_date: Optional[date] = None
    deadline_date: date
    expiration_date: date
    status: CourseEnrollmentStatus = Field(default=CourseEnrollmentStatus.PENDING)
    inspector_id: Optional[int] = Field(default=None, foreign_key="inspector.id")
    judge_id: Optional[int] = Field(default=None, foreign_key="judge.id")

class CourseEnrollmentCreate(CourseEnrollmentBase):
    pass

class CourseEnrollmentRead(CourseEnrollmentBase):
    id: int

class CourseEnrollmentUpdate(SQLModel):
    completion_date: Optional[date] = None
    status: Optional[CourseEnrollmentStatus] = None
    inspector_id: Optional[int] = None
    judge_id: Optional[int] = None
    deadline_date: Optional[date] = None
    expiration_date: Optional[date] = None

class CourseEnrollment(CourseEnrollmentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relaciones
    person: "Person" = Relationship(
        back_populates="course_enrollments",
        sa_relationship=sa_relationship("Person", back_populates="course_enrollments")
    )
    course: "TrafficSafetyCourse" = Relationship(
        back_populates="course_enrollments",
        sa_relationship=sa_relationship("TrafficSafetyCourse", back_populates="course_enrollments")
    )
    inspector: Optional["Inspector"] = Relationship(
        back_populates="used_enrollments",
        sa_relationship=sa_relationship("Inspector", back_populates="used_enrollments")
    )
    judge: Optional["Judge"] = Relationship(
        back_populates="used_enrollments",
        sa_relationship=sa_relationship("Judge", back_populates="used_enrollments")
    )