# app/routers/judge_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional

from app.config.database import get_session
from app.models import Judge, JudgeCreate, JudgeRead, JudgeUpdate, User

from app.services import judge_service
from app.routers.user_router import get_current_user, get_current_admin_user

router = APIRouter(prefix="/judges", tags=["Judges"])

@router.post("/", response_model=JudgeRead, status_code=status.HTTP_201_CREATED)
def create_judge(
    judge_create: JudgeCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Crea un nuevo juez.
    Requiere rol de Administrador.
    """
    try:
        new_judge = judge_service.create_judge(judge_create, session)
        return new_judge
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=List[JudgeRead])
def read_all_judges(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene una lista de todos los jueces.
    Requiere autenticación.
    """
    return judge_service.get_all_judges(session)

@router.get("/{judge_id}", response_model=JudgeRead)
def read_judge(
    judge_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene un juez por su ID.
    Requiere autenticación.
    """
    judge = judge_service.get_judge_by_id(judge_id, session)
    if not judge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Judge not found")
    return judge

@router.put("/{judge_id}", response_model=JudgeRead)
def update_judge(
    judge_id: int,
    updated_data: JudgeUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Actualiza un juez existente por su ID.
    Requiere rol de Administrador.
    """
    judge = judge_service.update_judge(judge_id, updated_data, session)
    if not judge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Judge not found")
    return judge

@router.delete("/{judge_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_judge(
    judge_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Elimina un juez por su ID.
    Requiere rol de Administrador.
    """
    if not judge_service.delete_judge(judge_id, session):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Judge not found")
    return
