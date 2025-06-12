from __future__ import annotations

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List 




class Inspector(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    
    # Un inspector puede haber "usado" muchas inscripciones
    used_enrollments: List["CourseEnrollment"] = Relationship(back_populates="inspector")