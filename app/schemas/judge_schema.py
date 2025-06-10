from sqlmodel import SQLModel

class JudgeCreate(SQLModel):
    name: str

class JudgeRead(SQLModel):
    id: int
    name: str

class JudgeUpdate(SQLModel):
    name: str | None = None