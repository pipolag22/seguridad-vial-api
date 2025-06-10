from sqlmodel import SQLModel

class InspectorCreate(SQLModel):
    name: str

class InspectorRead(SQLModel):
    id: int
    name: str

class InspectorUpdate(SQLModel):
    name: str | None = None