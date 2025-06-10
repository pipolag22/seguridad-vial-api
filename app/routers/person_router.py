from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.config.database import get_session
from app.schemas.person_schema import PersonCreate, PersonRead, PersonUpdate
from app.services import person_service # Importa el servicio
from typing import List

router = APIRouter(prefix="/persons", tags=["Persons"])

@router.post("/", response_model=PersonRead, status_code=status.HTTP_201_CREATED)
def create_person(person: PersonCreate, session: Session = Depends(get_session)):
    db_person = person_service.create_person(person, session)
    return db_person

@router.get("/", response_model=List[PersonRead])
def read_all_persons(session: Session = Depends(get_session)):
    return person_service.get_all_persons(session)

@router.get("/{person_id}", response_model=PersonRead)
def read_person(person_id: int, session: Session = Depends(get_session)):
    person = person_service.get_person_by_id(person_id, session)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person

@router.put("/{person_id}", response_model=PersonRead)
def update_person(person_id: int, person_update: PersonUpdate, session: Session = Depends(get_session)):
    updated_person = person_service.update_person(person_id, person_update, session)
    if not updated_person:
        raise HTTPException(status_code=404, detail="Person not found")
    return updated_person

@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_person(person_id: int, session: Session = Depends(get_session)):
    if not person_service.delete_person(person_id, session):
        raise HTTPException(status_code=404, detail="Person not found")
    return {"message": "Person deleted successfully"}