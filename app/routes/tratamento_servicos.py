
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from ..crud import tratamento_servicos as crud
from ..schemas import tratamento_servicos as schemas
from ..db.database import get_db
from ..routes.auth import get_current_active_user # Import get_current_active_user
from ..models.users import SystemUser # Import SystemUser

router = APIRouter()

@router.post("/tratamentos/{tratamento_id}/servicos", response_model=schemas.TratamentoServico, status_code=status.HTTP_201_CREATED, tags=["Tratamentos Servicos"])
async def add_servico_to_tratamento(
    tratamento_id: uuid.UUID,
    servico: schemas.TratamentoServicoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(get_current_active_user) # Add current_user dependency
):
    """Adds a service to a treatment plan."""
    tenant_id = current_user.default_tenant_id # Get tenant_id from current_user
    result = await crud.add_servico_to_tratamento(
        db=db, 
        tratamento_id=tratamento_id, 
        servico_id=servico.servico_id, 
        quantidade=servico.quantidade, 
        tenant_id=tenant_id
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Tratamento not found")
    return result

@router.get("/tratamentos/{tratamento_id}/servicos", response_model=List[schemas.TratamentoServico], tags=["Tratamentos Servicos"])
async def get_servicos_for_tratamento(
    tratamento_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(get_current_active_user) # Add current_user dependency
):
    """Gets all services associated with a treatment plan."""
    tenant_id = current_user.default_tenant_id # Get tenant_id from current_user
    return await crud.get_servicos_for_tratamento(db=db, tratamento_id=tratamento_id, tenant_id=tenant_id)

@router.delete("/tratamentos/{tratamento_id}/servicos/{servico_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tratamentos Servicos"])
async def remove_servico_from_tratamento(
    tratamento_id: uuid.UUID,
    servico_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(get_current_active_user) # Add current_user dependency
):
    """Removes a service from a treatment plan."""
    tenant_id = current_user.default_tenant_id # Get tenant_id from current_user
    result = await crud.remove_servico_from_tratamento(
        db=db, 
        tratamento_id=tratamento_id, 
        servico_id=servico_id, 
        tenant_id=tenant_id
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Association not found")
    return
