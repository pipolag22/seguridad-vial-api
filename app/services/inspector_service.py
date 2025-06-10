from sqlmodel import Session, select
from app.models.inspector import Inspector
from app.schemas.inspector_schema import InspectorCreate, InspectorRead, InspectorUpdate
from typing import List, Optional

def create_inspector(inspector_data: InspectorCreate, session: Session) -> InspectorRead:
    """Crea un nuevo inspector en la base de datos."""
    db_inspector = Inspector.model_validate(inspector_data)
    session.add(db_inspector)
    session.commit()
    session.refresh(db_inspector)
    return InspectorRead.model_validate(db_inspector)

def get_all_inspectors(session: Session) -> List[InspectorRead]:
    """Obtiene una lista de todos los inspectores."""
    inspectors = session.exec(select(Inspector)).all()
    return [InspectorRead.model_validate(i) for i in inspectors]

def get_inspector_by_id(inspector_id: int, session: Session) -> Optional[InspectorRead]:
    """Obtiene un inspector por su ID."""
    inspector = session.get(Inspector, inspector_id)
    if inspector:
        return InspectorRead.model_validate(inspector)
    return None

def update_inspector(inspector_id: int, inspector_data: InspectorUpdate, session: Session) -> Optional[InspectorRead]:
    """Actualiza un inspector existente."""
    inspector = session.get(Inspector, inspector_id)
    if not inspector:
        return None
    
    
    update_data = inspector_data.model_dump(exclude_unset=True)
    
   
    for key, value in update_data.items():
        setattr(inspector, key, value)
    
    session.add(inspector) 
    session.commit()
    session.refresh(inspector) 
    return InspectorRead.model_validate(inspector)

def delete_inspector(inspector_id: int, session: Session) -> bool:
    """Elimina un inspector por su ID."""
    inspector = session.get(Inspector, inspector_id)
    if not inspector:
        return False
    session.delete(inspector)
    session.commit()
    return True