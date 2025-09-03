from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid

from ..crud import tratamentos as tratamentos_crud
from ..schemas import tratamentos as tratamentos_schemas
from ..db.database import get_db
from ..routes.auth import get_current_active_user
from ..models.users import SystemUser
from ..core.permissions import can_create_treatment, can_read_treatment, can_update_treatment, can_delete_treatment, can_finalize_treatment, can_activate_treatment

router = APIRouter()

@router.post("/", response_model=tratamentos_schemas.Tratamento, status_code=status.HTTP_201_CREATED, tags=["Tratamentos"])
async def create_tratamento(
    tratamento: tratamentos_schemas.TratamentoCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: SystemUser = Depends(can_create_treatment)
):
    tenant_id = current_user.default_tenant_id
    return await tratamentos_crud.create_tratamento(db=db, tratamento=tratamento, tenant_id=tenant_id)

@router.get("/{tratamento_id}", response_model=tratamentos_schemas.Tratamento, tags=["Tratamentos"])
async def read_tratamento(
    tratamento_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user: SystemUser = Depends(can_read_treatment)
):
    tenant_id = current_user.default_tenant_id
    db_tratamento = await tratamentos_crud.get_tratamento(db, tratamento_id=tratamento_id, tenant_id=tenant_id)
    if db_tratamento is None:
        raise HTTPException(status_code=404, detail="Tratamento not found")
    return db_tratamento

@router.get("/", response_model=List[tratamentos_schemas.Tratamento], tags=["Tratamentos"])
async def read_tratamentos(
    skip: int = 0, 
    limit: int = 100, 
    paciente_id: Optional[uuid.UUID] = None, 
    db: AsyncSession = Depends(get_db), 
    current_user: SystemUser = Depends(can_read_treatment)
):
    tenant_id = current_user.default_tenant_id
    tratamentos = await tratamentos_crud.get_tratamentos(db, tenant_id=tenant_id, paciente_id=paciente_id, skip=skip, limit=limit)
    return tratamentos

@router.put("/{tratamento_id}", response_model=tratamentos_schemas.Tratamento, tags=["Tratamentos"])
async def update_tratamento(
    tratamento_id: uuid.UUID, 
    tratamento: tratamentos_schemas.TratamentoUpdate, 
    db: AsyncSession = Depends(get_db), 
    current_user: SystemUser = Depends(can_update_treatment)
):
    tenant_id = current_user.default_tenant_id
    db_tratamento = await tratamentos_crud.update_tratamento(db, tratamento_id=tratamento_id, tratamento_data=tratamento, tenant_id=tenant_id)
    if db_tratamento is None:
        raise HTTPException(status_code=404, detail="Tratamento not found")
    return db_tratamento

@router.delete("/{tratamento_id}", response_model=tratamentos_schemas.Tratamento, tags=["Tratamentos"])
async def delete_tratamento(
    tratamento_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user: SystemUser = Depends(can_delete_treatment)
):
    tenant_id = current_user.default_tenant_id
    db_tratamento = await tratamentos_crud.delete_tratamento(db, tratamento_id=tratamento_id, tenant_id=tenant_id)
    if db_tratamento is None:
        raise HTTPException(status_code=404, detail="Tratamento not found")
    return db_tratamento

@router.post("/{tratamento_id}/finalizar", response_model=tratamentos_schemas.Tratamento, tags=["Tratamentos"])
async def finalizar_tratamento(
    tratamento_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user: SystemUser = Depends(can_finalize_treatment)
):
    tenant_id = current_user.default_tenant_id
    db_tratamento = await tratamentos_crud.finalizar_tratamento(db, tratamento_id=tratamento_id, tenant_id=tenant_id)
    if db_tratamento is None:
        raise HTTPException(status_code=404, detail="Tratamento not found")
    return db_tratamento

@router.post("/{tratamento_id}/cancelar", response_model=tratamentos_schemas.Tratamento, tags=["Tratamentos"])
async def cancelar_tratamento(
    tratamento_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user: SystemUser = Depends(can_update_treatment)
):
    tenant_id = current_user.default_tenant_id
    db_tratamento = await tratamentos_crud.cancelar_tratamento(db, tratamento_id=tratamento_id, tenant_id=tenant_id)
    if db_tratamento is None:
        raise HTTPException(status_code=404, detail="Tratamento not found")
    return db_tratamento

@router.post("/{tratamento_id}/ativar", response_model=tratamentos_schemas.Tratamento, tags=["Tratamentos"])
async def ativar_tratamento(
    tratamento_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_activate_treatment)
):
    tenant_id = current_user.default_tenant_id
    db_tratamento = await tratamentos_crud.ativar_tratamento(
        db, tratamento_id=tratamento_id, tenant_id=tenant_id
    )
    if db_tratamento is None:
        raise HTTPException(status_code=404, detail="Tratamento not found")
    return db_tratamento
