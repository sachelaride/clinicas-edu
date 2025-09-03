
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from ..crud import pagamentos as crud
from ..schemas import pagamentos as schemas
from ..db.database import get_db
from ..routes.auth import get_current_active_user # Import get_current_active_user
from ..models.users import SystemUser # Import SystemUser

from ..core.permissions import can_manage_payments

router = APIRouter()

@router.post("/pagamentos/", response_model=schemas.Pagamento, status_code=status.HTTP_201_CREATED, tags=["Pagamentos"])
async def create_pagamento(
    pagamento: schemas.PagamentoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_manage_payments)
):
    tenant_id = current_user.default_tenant_id
    return await crud.create_pagamento(db=db, pagamento=pagamento, tenant_id=tenant_id)

@router.get("/pagamentos/paciente/{paciente_id}", response_model=List[schemas.Pagamento], tags=["Pagamentos"])
async def read_pagamentos_by_paciente(
    paciente_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_manage_payments)
):
    tenant_id = current_user.default_tenant_id
    return await crud.get_pagamentos_by_paciente(db, paciente_id=paciente_id, tenant_id=tenant_id, skip=skip, limit=limit)

@router.get("/pagamentos/{pagamento_id}", response_model=schemas.Pagamento, tags=["Pagamentos"])
async def read_pagamento(
    pagamento_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_manage_payments)
):
    tenant_id = current_user.default_tenant_id
    db_pagamento = await crud.get_pagamento(db, pagamento_id=pagamento_id, tenant_id=tenant_id)
    if db_pagamento is None:
        raise HTTPException(status_code=404, detail="Pagamento not found")
    return db_pagamento

@router.put("/pagamentos/{pagamento_id}", response_model=schemas.Pagamento, tags=["Pagamentos"])
async def update_pagamento(
    pagamento_id: uuid.UUID,
    pagamento: schemas.PagamentoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_manage_payments)
):
    tenant_id = current_user.default_tenant_id
    db_pagamento = await crud.update_pagamento(db, pagamento_id=pagamento_id, pagamento_data=pagamento, tenant_id=tenant_id)
    if db_pagamento is None:
        raise HTTPException(status_code=404, detail="Pagamento not found")
    return db_pagamento

@router.delete("/pagamentos/{pagamento_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Pagamentos"])
async def delete_pagamento(
    pagamento_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_manage_payments)
):
    tenant_id = current_user.default_tenant_id
    db_pagamento = await crud.delete_pagamento(db, pagamento_id=pagamento_id, tenant_id=tenant_id)
    if db_pagamento is None:
        raise HTTPException(status_code=404, detail="Pagamento not found")
    return
