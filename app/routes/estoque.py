
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from ..crud import estoque as crud
from ..schemas import estoque as schemas, movimentacoes_estoque as mov_schemas
from ..db.database import get_db
from ..routes.auth import get_current_active_user
from ..models.users import SystemUser
from ..core.permissions import can_create_update_stock, can_read_stock, can_manage_stock

router = APIRouter()

# Estoque endpoints
@router.post("/", response_model=schemas.Estoque, status_code=status.HTTP_201_CREATED, tags=["Estoque"])
async def create_estoque_item(
    item: schemas.EstoqueCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: SystemUser = Depends(can_create_update_stock)
):
    tenant_id = current_user.default_tenant_id
    return await crud.create_estoque_item(db=db, item=item, tenant_id=tenant_id)

@router.get("/", response_model=List[schemas.Estoque], tags=["Estoque"])
async def read_estoque_itens(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db), 
    current_user: SystemUser = Depends(can_read_stock)
):
    tenant_id = current_user.default_tenant_id
    return await crud.get_estoque_itens(db, tenant_id=tenant_id, skip=skip, limit=limit)

@router.get("/{item_id}", response_model=schemas.Estoque, tags=["Estoque"])
async def read_estoque_item(
    item_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user: SystemUser = Depends(can_read_stock)
):
    tenant_id = current_user.default_tenant_id
    db_item = await crud.get_estoque_item(db, item_id=item_id, tenant_id=tenant_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item de estoque não encontrado")
    return db_item

@router.put("/{item_id}", response_model=schemas.Estoque, tags=["Estoque"])
async def update_estoque_item(
    item_id: uuid.UUID, 
    item: schemas.EstoqueUpdate, 
    db: AsyncSession = Depends(get_db), 
    current_user: SystemUser = Depends(can_create_update_stock)
):
    tenant_id = current_user.default_tenant_id
    db_item = await crud.update_estoque_item(db, item_id=item_id, item_data=item, tenant_id=tenant_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item de estoque não encontrado")
    return db_item

@router.delete("/{item_id}", response_model=schemas.Estoque, tags=["Estoque"])
async def delete_estoque_item(
    item_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user: SystemUser = Depends(can_manage_stock)
):
    tenant_id = current_user.default_tenant_id
    db_item = await crud.delete_estoque_item(db, item_id=item_id, tenant_id=tenant_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item de estoque não encontrado")
    return db_item

# Movimentacoes de Estoque endpoints
@router.post("/movimentacoes/", response_model=mov_schemas.MovimentacaoEstoque, status_code=status.HTTP_201_CREATED, tags=["Estoque"])
async def create_movimentacao(
    movimentacao: mov_schemas.MovimentacaoEstoqueCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_create_update_stock)
):
    tenant_id = current_user.default_tenant_id
    return await crud.create_movimentacao(db=db, movimentacao=movimentacao, tenant_id=tenant_id)

@router.get("/{produto_id}/movimentacoes/", response_model=List[mov_schemas.MovimentacaoEstoque], tags=["Estoque"])
async def read_movimentacoes_for_item(
    produto_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_read_stock)
):
    tenant_id = current_user.default_tenant_id
    return await crud.get_movimentacoes_for_item(db, produto_id=produto_id, tenant_id=tenant_id, skip=skip, limit=limit)

@router.get("/pacientes/{paciente_id}/movimentacoes/", response_model=List[mov_schemas.MovimentacaoEstoque], tags=["Estoque"])
async def read_movimentacoes_for_paciente(
    paciente_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_read_stock)
):
    tenant_id = current_user.default_tenant_id
    return await crud.get_movimentacoes_for_paciente(db, paciente_id=paciente_id, tenant_id=tenant_id, skip=skip, limit=limit)
