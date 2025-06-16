from __future__ import annotations
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.orm import relationship as sa_relationship
from sqlmodel import Field, SQLModel




class PersonBase(SQLModel):
    name: str = Field(..., max_length=100, index=True)
    dni: str = Field(..., max_length=20, unique=True)

class PersonCreate(PersonBase):
    pass

class PersonRead(PersonBase):
    id: int

class PersonUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=100)
    dni: Optional[str] = Field(default=None, max_length=20)

class Person(PersonBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relación con CourseEnrollment
    course_enrollments: List["CourseEnrollment"] = Relationship(
        back_populates="person",
        sa_relationship=sa_relationship("CourseEnrollment", back_populates="person")
    )