# app/routers/inspector_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional

from app.config.database import get_session
from app.models import Inspector, InspectorCreate, InspectorRead, InspectorUpdate, User

from app.services import inspector_service
from app.routers.user_router import get_current_user, get_current_admin_user

router = APIRouter(prefix="/inspectors", tags=["Inspectors"])

@router.post("/", response_model=InspectorRead, status_code=status.HTTP_201_CREATED)
def create_inspector(
    inspector_create: InspectorCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Crea un nuevo inspector.
    Requiere rol de Administrador.
    """
    try:
        new_inspector = inspector_service.create_inspector(inspector_create, session)
        return new_inspector
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=List[InspectorRead])
def read_all_inspectors(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene una lista de todos los inspectores.
    Requiere autenticación.
    """
    return inspector_service.get_all_inspectors(session)

@router.get("/{inspector_id}", response_model=InspectorRead)
def read_inspector(
    inspector_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene un inspector por su ID.
    Requiere autenticación.
    """
    inspector = inspector_service.get_inspector_by_id(inspector_id, session)
    if not inspector:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspector not found")
    return inspector

@router.put("/{inspector_id}", response_model=InspectorRead)
def update_inspector(
    inspector_id: int,
    updated_data: InspectorUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Actualiza un inspector existente por su ID.
    Requiere rol de Administrador.
    """
    inspector = inspector_service.update_inspector(inspector_id, updated_data, session)
    if not inspector:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspector not found")
    return inspector

@router.delete("/{inspector_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inspector(
    inspector_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Elimina un inspector por su ID.
    Requiere rol de Administrador.
    """
    if not inspector_service.delete_inspector(inspector_id, session):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspector not found")
    return
