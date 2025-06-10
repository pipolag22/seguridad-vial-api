from sqlmodel import SQLModel

class PersonCreate(SQLModel):
    name: str
    dni: str

class PersonRead(SQLModel):
    id: int
    name: str
    dni: str

class PersonUpdate(SQLModel):
    name: str | None = None
    dni: str | None = None