from sqlmodel import Field, Relationship, SQLModel, Enum
from datetime import date
from typing import List, Optional
from enum import Enum as PyEnum 

from app.models.person import PersonRead
from app.models.traffic_safety_course import TrafficSafetyCourseRead


class CourseEnrollmentStatus(PyEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELED = "canceled"
    ACTIVE = "active"


class CourseEnrollmentBase(SQLModel):
    enrollment_date: date = Field(default_factory=date.today) 
    completion_date: Optional[date] = None
    expiration_date: Optional[date] = None 
    status: CourseEnrollmentStatus = CourseEnrollmentStatus.PENDING
    notes: Optional[str] = None
    person_id: int = Field(foreign_key="person.id")
    course_id: int = Field(foreign_key="trafficsafetycourse.id")


class CourseEnrollment(CourseEnrollmentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # Relaciones
    person: "Person" = Relationship(back_populates="course_enrollments")
    course: "TrafficSafetyCourse" = Relationship(back_populates="course_enrollments")


class CourseEnrollmentCreate(CourseEnrollmentBase):
    pass


class CourseEnrollmentRead(CourseEnrollmentBase):
    id: int

    person: PersonRead
    course: TrafficSafetyCourseRead


class CourseEnrollmentUpdate(SQLModel):
    enrollment_date: Optional[date] = None
    completion_date: Optional[date] = None
    expiration_date: Optional[date] = None
    status: Optional[CourseEnrollmentStatus] = None
    notes: Optional[str] = None
    person_id: Optional[int] = None
    course_id: Optional[int] = None



class CourseEnrollmentReportItem(SQLModel):
    id: int
    enrollment_date: date
    completion_date: Optional[date] = None
    expiration_date: date
    status: CourseEnrollmentStatus
    notes: Optional[str] = None
    
    person: PersonRead 

    course: TrafficSafetyCourseRead 
   
    days_until_expiration: Optional[int] = None
    is_expired: bool = False