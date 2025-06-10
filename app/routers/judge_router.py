from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models.judge import Judge
from app.config.database import get_session
from typing import List

router = APIRouter(prefix="/judges", tags=["Judges"])

@router.post("/", response_model=Judge)
def create_judge(judge: Judge, session: Session = Depends(get_session)):
    session.add(judge)
    session.commit()
    session.refresh(judge)
    return judge

@router.get("/", response_model=List[Judge])
def read_all_judges(session: Session = Depends(get_session)):
    return session.exec(select(Judge)).all()

@router.get("/{judge_id}", response_model=Judge)
def read_judge(judge_id: int, session: Session = Depends(get_session)):
    judge = session.get(Judge, judge_id)
    if not judge:
        raise HTTPException(status_code=404, detail="Judge not found")
    return judge

@router.delete("/{judge_id}")
def delete_judge(judge_id: int, session: Session = Depends(get_session)):
    judge = session.get(Judge, judge_id)
    if not judge:
        raise HTTPException(status_code=404, detail="Judge not found")
    session.delete(judge)
    session.commit()
    return {"deleted": True}
