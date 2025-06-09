from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models.person import Person
from app.config.database import get_session
from typing import List

router = APIRouter(prefix="/persons", tags=["Persons"])

@router.post("/", response_model=Person)
def create_person(person: Person, session: Session = Depends(get_session)):
    session.add(person)
    session.commit()
    session.refresh(person)
    return person

@router.get("/", response_model=List[Person])
def read_all_persons(session: Session = Depends(get_session)):
    return session.exec(select(Person)).all()

@router.get("/{person_id}", response_model=Person)
def read_person(person_id: int, session: Session = Depends(get_session)):
    person = session.get(Person, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person

@router.put("/{person_id}", response_model=Person)
def update_person(person_id: int, updated: Person, session: Session = Depends(get_session)):
    person = session.get(Person, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    person.name = updated.name
    person.dni = updated.dni
    session.commit()
    session.refresh(person)
    return person

@router.delete("/{person_id}")
def delete_person(person_id: int, session: Session = Depends(get_session)):
    person = session.get(Person, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    session.delete(person)
    session.commit()
    return {"deleted": True}
