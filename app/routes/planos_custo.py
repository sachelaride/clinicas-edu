
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from ..crud import planos_custo as crud
from ..schemas import planos_custo as schemas
from ..schemas import planos_custo_itens as item_schemas
from ..db.database import get_db
from ..routes.auth import get_current_active_user
from ..models.users import SystemUser
from ..core.permissions import can_create_update_cost_plans, can_read_cost_plans, can_manage_cost_plans

router = APIRouter()

# Plano de Custo endpoints
@router.post("/planos-custo/", response_model=schemas.PlanoCusto, status_code=status.HTTP_201_CREATED, tags=["Planos de Custo"])
async def create_plano_custo(
    plano_custo: schemas.PlanoCustoCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: SystemUser = Depends(can_create_update_cost_plans)
):
    tenant_id = current_user.default_tenant_id
    return await crud.create_plano_custo(db=db, plano_custo=plano_custo, tenant_id=tenant_id)

@router.get("/planos-custo/", response_model=List[schemas.PlanoCusto], tags=["Planos de Custo"])
async def read_planos_custo(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db), 
    current_user: SystemUser = Depends(can_read_cost_plans)
):
    tenant_id = current_user.default_tenant_id
    return await crud.get_planos_custo(db, tenant_id=tenant_id, skip=skip, limit=limit)

@router.get("/planos-custo/{plano_custo_id}", response_model=schemas.PlanoCusto, tags=["Planos de Custo"])
async def read_plano_custo(
    plano_custo_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user: SystemUser = Depends(can_read_cost_plans)
):
    tenant_id = current_user.default_tenant_id
    db_plano_custo = await crud.get_plano_custo(db, plano_custo_id=plano_custo_id, tenant_id=tenant_id)
    if db_plano_custo is None:
        raise HTTPException(status_code=404, detail="Plano de Custo not found")
    return db_plano_custo

@router.put("/planos-custo/{plano_custo_id}", response_model=schemas.PlanoCusto, tags=["Planos de Custo"])
async def update_plano_custo(
    plano_custo_id: uuid.UUID, 
    plano_custo: schemas.PlanoCustoUpdate, 
    db: AsyncSession = Depends(get_db), 
    current_user: SystemUser = Depends(can_create_update_cost_plans)
):
    tenant_id = current_user.default_tenant_id
    db_plano_custo = await crud.update_plano_custo(db, plano_custo_id=plano_custo_id, plano_custo_data=plano_custo, tenant_id=tenant_id)
    if db_plano_custo is None:
        raise HTTPException(status_code=404, detail="Plano de Custo not found")
    return db_plano_custo

@router.delete("/planos-custo/{plano_custo_id}", response_model=schemas.PlanoCusto, tags=["Planos de Custo"])
async def delete_plano_custo(
    plano_custo_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user: SystemUser = Depends(can_manage_cost_plans)
):
    tenant_id = current_user.default_tenant_id
    db_plano_custo = await crud.delete_plano_custo(db, plano_custo_id=plano_custo_id, tenant_id=tenant_id)
    if db_plano_custo is None:
        raise HTTPException(status_code=404, detail="Plano de Custo not found")
    return db_plano_custo

# Plano de Custo Itens endpoints
@router.post("/planos-custo/{plano_custo_id}/itens", response_model=item_schemas.PlanoCustoItem, status_code=status.HTTP_201_CREATED, tags=["Planos de Custo"])
async def add_item_to_plano_custo(
    plano_custo_id: uuid.UUID,
    item: item_schemas.PlanoCustoItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_create_update_cost_plans)
):
    tenant_id = current_user.default_tenant_id
    result = await crud.add_item_to_plano_custo(db=db, plano_custo_id=plano_custo_id, item=item, tenant_id=tenant_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Plano de Custo or Servico not found")
    return result

@router.delete("/planos-custo/{plano_custo_id}/itens/{item_id}", response_model=item_schemas.PlanoCustoItem, tags=["Planos de Custo"])
async def remove_item_from_plano_custo(
    plano_custo_id: uuid.UUID,
    item_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_create_update_cost_plans)
):
    tenant_id = current_user.default_tenant_id
    result = await crud.remove_item_from_plano_custo(db=db, plano_custo_id=plano_custo_id, item_id=item_id, tenant_id=tenant_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return result
