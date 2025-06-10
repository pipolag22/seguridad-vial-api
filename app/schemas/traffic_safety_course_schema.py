from sqlmodel import SQLModel

class TrafficSafetyCourseCreate(SQLModel):
    name: str
    description: str

class TrafficSafetyCourseRead(SQLModel):
    id: int
    name: str
    description: str

class TrafficSafetyCourseUpdate(SQLModel):
    name: str | None = None
    description: str | None = None