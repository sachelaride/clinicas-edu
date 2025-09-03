
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from ..crud import despesas as crud
from ..schemas import despesas as schemas
from ..db.database import get_db
from ..routes.auth import get_current_active_user # Import get_current_active_user
from ..models.users import SystemUser, UserRole
from ..core.permissions import has_permission

# Define permission for this module
can_manage_expenses = has_permission([UserRole.admin_global, UserRole.gestor_clinica])

router = APIRouter()

@router.post("/despesas/", response_model=schemas.Despesa, status_code=status.HTTP_201_CREATED, tags=["Despesas"])
async def create_despesa(
    despesa: schemas.DespesaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_manage_expenses)
):
    tenant_id = current_user.default_tenant_id
    return await crud.create_despesa(db=db, despesa=despesa, tenant_id=tenant_id)

@router.get("/despesas/", response_model=List[schemas.Despesa], tags=["Despesas"])
async def read_despesas(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_manage_expenses)
):
    tenant_id = current_user.default_tenant_id
    return await crud.get_despesas(db, tenant_id=tenant_id, skip=skip, limit=limit)

@router.get("/despesas/{despesa_id}", response_model=schemas.Despesa, tags=["Despesas"])
async def read_despesa(
    despesa_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_manage_expenses)
):
    tenant_id = current_user.default_tenant_id
    db_despesa = await crud.get_despesa(db, despesa_id=despesa_id, tenant_id=tenant_id)
    if db_despesa is None:
        raise HTTPException(status_code=404, detail="Despesa not found")
    return db_despesa

@router.put("/despesas/{despesa_id}", response_model=schemas.Despesa, tags=["Despesas"])
async def update_despesa(
    despesa_id: uuid.UUID,
    despesa: schemas.DespesaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_manage_expenses)
):
    tenant_id = current_user.default_tenant_id
    db_despesa = await crud.update_despesa(db, despesa_id=despesa_id, despesa_data=despesa, tenant_id=tenant_id)
    if db_despesa is None:
        raise HTTPException(status_code=404, detail="Despesa not found")
    return db_despesa

@router.delete("/despesas/{despesa_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Despesas"])
async def delete_despesa(
    despesa_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_manage_expenses)
):
    tenant_id = current_user.default_tenant_id
    db_despesa = await crud.delete_despesa(db, despesa_id=despesa_id, tenant_id=tenant_id)
    if db_despesa is None:
        raise HTTPException(status_code=404, detail="Despesa not found")
    return
