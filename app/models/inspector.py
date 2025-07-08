# app/models/inspector.py
from __future__ import annotations

from sqlmodel import SQLModel, Field
from typing import Optional, List
# from sqlalchemy.orm import Mapped

class InspectorBase(SQLModel):
    name: str

class InspectorCreate(InspectorBase):
    pass

class InspectorRead(InspectorBase):
    id: int

class InspectorUpdate(SQLModel):
    name: Optional[str] = None

class Inspector(InspectorBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # RELACIÓN TEMPORALMENTE ELIMINADA
    # used_enrollments: Mapped[List["CourseEnrollment"]] = Relationship(back_populates="inspector")
