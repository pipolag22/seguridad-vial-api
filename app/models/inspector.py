from __future__ import annotations
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.orm import relationship as sa_relationship


class InspectorBase(SQLModel):
    name: str = Field(index=True)

class InspectorCreate(InspectorBase):
    pass

class InspectorRead(InspectorBase):
    id: int

class InspectorUpdate(SQLModel):
    name: Optional[str] = Field(default=None, index=True)

class Inspector(InspectorBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    used_enrollments: List["CourseEnrollment"] = Relationship(
        back_populates="inspector",
        sa_relationship=sa_relationship("CourseEnrollment", back_populates="inspector")
    )