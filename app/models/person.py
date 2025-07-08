# app/models/person.py
from __future__ import annotations

from sqlmodel import SQLModel, Field
from typing import Optional, List
# from sqlalchemy.orm import Mapped # No necesitamos Mapped si no hay Relationship

class PersonBase(SQLModel):
    name: str
    dni: str

class PersonCreate(PersonBase):
    pass

class PersonRead(PersonBase):
    id: int

class PersonUpdate(SQLModel):
    name: Optional[str] = None
    dni: Optional[str] = None

class Person(PersonBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # RELACIÓN TEMPORALMENTE ELIMINADA
    # course_enrollments: Mapped[List["CourseEnrollment"]] = Relationship(back_populates="person")
