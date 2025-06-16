from sqlmodel import Session, select
from typing import List, Optional

from app.models import Judge, JudgeCreate, JudgeRead, JudgeUpdate

def create_judge(judge_create: JudgeCreate, session: Session) -> Judge:
    """
    Crea un nuevo juez en la base de datos.
    """
    new_judge = Judge.from_orm(judge_create) # Usar from_orm para Pydantic V1
    session.add(new_judge)
    session.commit()
    session.refresh(new_judge)
    return new_judge

def get_judge_by_id(judge_id: int, session: Session) -> Optional[Judge]:
    """
    Obtiene un juez por su ID.
    """
    return session.get(Judge, judge_id)

def get_all_judges(session: Session) -> List[Judge]:
    """
    Obtiene todos los jueces de la base de datos.
    """
    return session.exec(select(Judge)).all()

def update_judge(judge_id: int, judge_update_data: JudgeUpdate, session: Session) -> Optional[Judge]:
    """
    Actualiza un juez existente por su ID.
    """
    judge = session.get(Judge, judge_id)
    if not judge:
        return None
    
    # Usar .dict(exclude_unset=True) para Pydantic V1
    for key, value in judge_update_data.dict(exclude_unset=True).items():
        setattr(judge, key, value)
    
    session.add(judge)
    session.commit()
    session.refresh(judge)
    return judge

def delete_judge(judge_id: int, session: Session) -> bool:
    """
    Elimina un juez por su ID.
    """
    judge = session.get(Judge, judge_id)
    if not judge:
        return False
    session.delete(judge)
    session.commit()
    return True