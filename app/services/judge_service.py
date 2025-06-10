from sqlmodel import Session, select
from app.models.judge import Judge
from app.schemas.judge_schema import JudgeCreate, JudgeRead, JudgeUpdate
from typing import List, Optional

def create_judge(judge_data: JudgeCreate, session: Session) -> JudgeRead:
    """Crea un nuevo juez en la base de datos."""
    db_judge = Judge.model_validate(judge_data)
    session.add(db_judge)
    session.commit()
    session.refresh(db_judge)
    return JudgeRead.model_validate(db_judge)

def get_all_judges(session: Session) -> List[JudgeRead]:
    """Obtiene una lista de todos los jueces."""
    judges = session.exec(select(Judge)).all()
    return [JudgeRead.model_validate(j) for j in judges]

def get_judge_by_id(judge_id: int, session: Session) -> Optional[JudgeRead]:
    """Obtiene un juez por su ID."""
    judge = session.get(Judge, judge_id)
    if judge:
        return JudgeRead.model_validate(judge)
    return None

def update_judge(judge_id: int, judge_data: JudgeUpdate, session: Session) -> Optional[JudgeRead]:
    """Actualiza un juez existente."""
    judge = session.get(Judge, judge_id)
    if not judge:
        return None
    
    update_data = judge_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(judge, key, value)
    
    session.add(judge)
    session.commit()
    session.refresh(judge)
    return JudgeRead.model_validate(judge)

def delete_judge(judge_id: int, session: Session) -> bool:
    """Elimina un juez por su ID."""
    judge = session.get(Judge, judge_id)
    if not judge:
        return False
    session.delete(judge)
    session.commit()
    return True