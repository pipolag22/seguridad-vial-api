from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date

class CourseEnrollment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    person_id: int = Field(foreign_key="person.id")
    course_id: int = Field(foreign_key="trafficsafetycourse.id")
    enrollment_date: date
    deadline_date: date
    expiration_date: date
    status: str  # pending, completed, used, expired
    inspector_id: Optional[int] = Field(default=None, foreign_key="inspector.id")
    judge_id: Optional[int] = Field(default=None, foreign_key="judge.id")