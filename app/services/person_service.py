from sqlmodel import Session, select
from app.models.person import Person
from app.schemas.person_schema import PersonCreate, PersonRead, PersonUpdate
from typing import List, Optional

def create_person(person_data: PersonCreate, session: Session) -> PersonRead:
    db_person = Person.model_validate(person_data)
    session.add(db_person)
    session.commit()
    session.refresh(db_person)
    return PersonRead.model_validate(db_person)

def get_all_persons(session: Session) -> List[PersonRead]:
    persons = session.exec(select(Person)).all()
    return [PersonRead.model_validate(p) for p in persons]

def get_person_by_id(person_id: int, session: Session) -> Optional[PersonRead]:
    person = session.get(Person, person_id)
    if person:
        return PersonRead.model_validate(person)
    return None

def update_person(person_id: int, person_data: PersonUpdate, session: Session) -> Optional[PersonRead]:
    person = session.get(Person, person_id)
    if not person:
        return None

    
    update_data = person_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(person, key, value)

    session.add(person)
    session.commit()
    session.refresh(person)
    return PersonRead.model_validate(person)

def delete_person(person_id: int, session: Session) -> bool:
    person = session.get(Person, person_id)
    if not person:
        return False
    session.delete(person)
    session.commit()
    return True