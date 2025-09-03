from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from ..crud import feriados as crud
from ..schemas import feriados as schemas
from ..db.database import get_db
from ..routes.auth import get_current_active_user
from ..models.users import SystemUser
from ..core.permissions import can_manage_feriados

router = APIRouter()

@router.post("/feriados/", response_model=schemas.Feriado, status_code=status.HTTP_201_CREATED, tags=["Feriados"])
async def create_feriado(
    feriado: schemas.FeriadoCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: SystemUser = Depends(can_manage_feriados)
):
    tenant_id = current_user.default_tenant_id
    return await crud.create_feriado(db=db, feriado=feriado, tenant_id=tenant_id)

@router.get("/feriados/", response_model=List[schemas.Feriado], tags=["Feriados"])
async def read_feriados(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db), 
    current_user: SystemUser = Depends(can_manage_feriados)
):
    tenant_id = current_user.default_tenant_id
    return await crud.get_feriados(db, tenant_id=tenant_id, skip=skip, limit=limit)

@router.get("/feriados/{feriado_id}", response_model=schemas.Feriado, tags=["Feriados"])
async def read_feriado(
    feriado_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user: SystemUser = Depends(can_manage_feriados)
):
    tenant_id = current_user.default_tenant_id
    db_feriado = await crud.get_feriado(db, feriado_id=feriado_id, tenant_id=tenant_id)
    if db_feriado is None:
        raise HTTPException(status_code=404, detail="Feriado não encontrado")
    return db_feriado

@router.put("/feriados/{feriado_id}", response_model=schemas.Feriado, tags=["Feriados"])
async def update_feriado(
    feriado_id: uuid.UUID, 
    feriado: schemas.FeriadoUpdate, 
    db: AsyncSession = Depends(get_db), 
    current_user: SystemUser = Depends(can_manage_feriados)
):
    tenant_id = current_user.default_tenant_id
    db_feriado = await crud.update_feriado(db, feriado_id=feriado_id, feriado_data=feriado, tenant_id=tenant_id)
    if db_feriado is None:
        raise HTTPException(status_code=404, detail="Feriado não encontrado")
    return db_feriado

@router.delete("/feriados/{feriado_id}", response_model=schemas.Feriado, tags=["Feriados"])
async def delete_feriado(
    feriado_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user: SystemUser = Depends(can_manage_feriados)
):
    tenant_id = current_user.default_tenant_id
    db_feriado = await crud.delete_feriado(db, feriado_id=feriado_id, tenant_id=tenant_id)
    if db_feriado is None:
        raise HTTPException(status_code=404, detail="Feriado não encontrado")
    return db_feriado
