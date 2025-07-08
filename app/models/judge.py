# app/models/judge.py
from __future__ import annotations

from sqlmodel import SQLModel, Field
from typing import Optional, List
# from sqlalchemy.orm import Mapped

class JudgeBase(SQLModel):
    name: str

class JudgeCreate(JudgeBase):
    pass

class JudgeRead(JudgeBase):
    id: int

class JudgeUpdate(SQLModel):
    name: Optional[str] = None

class Judge(JudgeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # RELACIÓN TEMPORALMENTE ELIMINADA
    # used_enrollments: Mapped[List["CourseEnrollment"]] = Relationship(back_populates="judge")
