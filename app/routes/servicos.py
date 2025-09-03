from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid

from ..crud import servicos as servicos_crud
from ..schemas import servicos as servicos_schemas
from ..db.database import get_db
from ..routes.auth import get_current_active_user
from ..models.users import SystemUser, UserRole
from ..core.permissions import can_create_update_services, can_read_services, can_manage_services

router = APIRouter()

@router.post("/", response_model=servicos_schemas.Servico, status_code=status.HTTP_201_CREATED, tags=["Servicos"])
async def create_servico(
    servico: servicos_schemas.ServicoCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: SystemUser = Depends(can_create_update_services)
):
    tenant_id = current_user.default_tenant_id
    return await servicos_crud.create_servico(db=db, servico=servico, tenant_id=tenant_id)

@router.get("/{servico_id}", response_model=servicos_schemas.Servico, tags=["Servicos"])
async def read_servico(
    servico_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user: SystemUser = Depends(can_read_services)
):
    tenant_id = current_user.default_tenant_id
    db_servico = await servicos_crud.get_servico(db, servico_id=servico_id, tenant_id=tenant_id)
    if db_servico is None:
        raise HTTPException(status_code=404, detail="Servico not found")
    return db_servico

@router.get("/", response_model=List[servicos_schemas.Servico], tags=["Servicos"])
async def read_servicos(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_read_services)
):
    tenant_id = current_user.default_tenant_id # Get tenant_id from current_user
    if current_user.role == UserRole.admin_global:
        servicos = await servicos_crud.get_servicos(db, tenant_id=None, skip=skip, limit=limit)
    else:
        servicos = await servicos_crud.get_servicos(db, tenant_id=tenant_id, skip=skip, limit=limit)
    return servicos

@router.put("/{servico_id}", response_model=servicos_schemas.Servico, tags=["Servicos"])
async def update_servico(
    servico_id: uuid.UUID, 
    servico: servicos_schemas.ServicoUpdate, 
    db: AsyncSession = Depends(get_db), 
    current_user: SystemUser = Depends(can_create_update_services)
):
    tenant_id = current_user.default_tenant_id
    db_servico = await servicos_crud.update_servico(db, servico_id=servico_id, servico_data=servico, tenant_id=tenant_id)
    if db_servico is None:
        raise HTTPException(status_code=404, detail="Servico not found")
    return db_servico

@router.delete("/{servico_id}", response_model=servicos_schemas.Servico, tags=["Servicos"])
async def delete_servico(
    servico_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user: SystemUser = Depends(can_manage_services)
):
    tenant_id = current_user.default_tenant_id
    db_servico = await servicos_crud.delete_servico(db, servico_id=servico_id, tenant_id=tenant_id)
    if db_servico is None:
        raise HTTPException(status_code=404, detail="Servico not found")
    return db_servico
