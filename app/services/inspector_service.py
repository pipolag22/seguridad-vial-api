# app/services/inspector_service.py

from sqlmodel import Session, select
from typing import List, Optional

from app.models import Inspector, InspectorCreate, InspectorRead, InspectorUpdate

def create_inspector(inspector_create: InspectorCreate, session: Session) -> Inspector:
    """
    Crea un nuevo inspector en la base de datos.
    """
    new_inspector = Inspector.from_orm(inspector_create) # Usar from_orm para Pydantic V1
    session.add(new_inspector)
    session.commit()
    session.refresh(new_inspector)
    return new_inspector

def get_inspector_by_id(inspector_id: int, session: Session) -> Optional[Inspector]:
    """
    Obtiene un inspector por su ID.
    """
    return session.get(Inspector, inspector_id)

def get_all_inspectors(session: Session) -> List[Inspector]:
    """
    Obtiene todos los inspectores de la base de datos.
    """
    return session.exec(select(Inspector)).all()

def update_inspector(inspector_id: int, inspector_update_data: InspectorUpdate, session: Session) -> Optional[Inspector]:
    """
    Actualiza un inspector existente por su ID.
    """
    inspector = session.get(Inspector, inspector_id)
    if not inspector:
        return None
    
    # Usar .dict(exclude_unset=True) para Pydantic V1
    for key, value in inspector_update_data.dict(exclude_unset=True).items():
        setattr(inspector, key, value)
    
    session.add(inspector)
    session.commit()
    session.refresh(inspector)
    return inspector

def delete_inspector(inspector_id: int, session: Session) -> bool:
    """
    Elimina un inspector por su ID.
    """
    inspector = session.get(Inspector, inspector_id)
    if not inspector:
        return False
    session.delete(inspector)
    session.commit()
    return True
