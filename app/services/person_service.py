from sqlmodel import Session, select
from typing import List, Optional

from app.models import Person, PersonCreate, PersonRead, PersonUpdate

def create_person(person_create: PersonCreate, session: Session) -> Person:
    """
    Crea una nueva persona en la base de datos.
    """
    new_person = Person.from_orm(person_create) # Usar from_orm para Pydantic V1
    session.add(new_person)
    session.commit()
    session.refresh(new_person)
    return new_person

def get_person_by_id(person_id: int, session: Session) -> Optional[Person]:
    """
    Obtiene una persona por su ID.
    """
    return session.get(Person, person_id)

def get_all_persons(session: Session) -> List[Person]:
    """
    Obtiene todas las personas de la base de datos.
    """
    return session.exec(select(Person)).all()

def update_person(person_id: int, person_update_data: PersonUpdate, session: Session) -> Optional[Person]:
    """
    Actualiza una persona existente por su ID.
    """
    person = session.get(Person, person_id)
    if not person:
        return None
    
    # Actualizar solo los campos proporcionados en person_update_data
    # Usar .dict(exclude_unset=True) para Pydantic V1
    for key, value in person_update_data.dict(exclude_unset=True).items():
        setattr(person, key, value)
    
    session.add(person)
    session.commit()
    session.refresh(person)
    return person

def delete_person(person_id: int, session: Session) -> bool:
    """
    Elimina una persona por su ID.
    """
    person = session.get(Person, person_id)
    if not person:
        return False
    session.delete(person)
    session.commit()
    return True
