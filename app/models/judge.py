from __future__ import annotations
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.orm import relationship as sa_relationship


class JudgeBase(SQLModel):
    name: str = Field(max_length=100, index=True)

class JudgeCreate(JudgeBase):
    pass

class JudgeRead(JudgeBase):
    id: int

class JudgeUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=100, description="Nombre del juez")

class Judge(JudgeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, description="ID único del juez")
    
    used_enrollments: List["CourseEnrollment"] = Relationship(
        back_populates="judge",
        sa_relationship=sa_relationship("CourseEnrollment", back_populates="judge")
    )