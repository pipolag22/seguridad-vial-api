from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models.inspector import Inspector
from app.config.database import get_session
from typing import List

router = APIRouter(prefix="/inspectors", tags=["Inspectors"])

@router.post("/", response_model=Inspector)
def create_inspector(inspector: Inspector, session: Session = Depends(get_session)):
    session.add(inspector)
    session.commit()
    session.refresh(inspector)
    return inspector

@router.get("/", response_model=List[Inspector])
def read_all_inspectors(session: Session = Depends(get_session)):
    return session.exec(select(Inspector)).all()

@router.get("/{inspector_id}", response_model=Inspector)
def read_inspector(inspector_id: int, session: Session = Depends(get_session)):
    inspector = session.get(Inspector, inspector_id)
    if not inspector:
        raise HTTPException(status_code=404, detail="Inspector not found")
    return inspector

@router.delete("/{inspector_id}")
def delete_inspector(inspector_id: int, session: Session = Depends(get_session)):
    inspector = session.get(Inspector, inspector_id)
    if not inspector:
        raise HTTPException(status_code=404, detail="Inspector not found")
    session.delete(inspector)
    session.commit()
    return {"deleted": True}
