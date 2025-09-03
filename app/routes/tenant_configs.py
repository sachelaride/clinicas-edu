
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from ..crud import tenant_configs as crud
from ..schemas import tenant_configs as schemas
from ..db.database import get_db
from ..routes.auth import get_current_active_user # Import get_current_active_user
from ..models.users import SystemUser # Import SystemUser

router = APIRouter()

@router.post("/tenant-configs/", response_model=schemas.TenantConfig, status_code=status.HTTP_201_CREATED, tags=["Tenant Configurations"])
async def create_tenant_config(config: schemas.TenantConfigCreate, db: AsyncSession = Depends(get_db), current_user: SystemUser = Depends(get_current_active_user)):
    tenant_id = current_user.default_tenant_id
    return await crud.create_tenant_config(db=db, config=config, tenant_id=tenant_id)

@router.get("/tenant-configs/", response_model=List[schemas.TenantConfig], tags=["Tenant Configurations"])
async def read_tenant_configs(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), current_user: SystemUser = Depends(get_current_active_user)):
    tenant_id = current_user.default_tenant_id
    return await crud.get_tenant_configs(db, tenant_id=tenant_id, skip=skip, limit=limit)

@router.get("/tenant-configs/{config_id}", response_model=schemas.TenantConfig, tags=["Tenant Configurations"])
async def read_tenant_config(config_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: SystemUser = Depends(get_current_active_user)):
    tenant_id = current_user.default_tenant_id
    db_config = await crud.get_tenant_config(db, config_id=config_id, tenant_id=tenant_id)
    if db_config is None:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")
    return db_config

@router.put("/tenant-configs/{config_id}", response_model=schemas.TenantConfig, tags=["Tenant Configurations"])
async def update_tenant_config(config_id: uuid.UUID, config: schemas.TenantConfigUpdate, db: AsyncSession = Depends(get_db), current_user: SystemUser = Depends(get_current_active_user)):
    tenant_id = current_user.default_tenant_id
    db_config = await crud.update_tenant_config(db, config_id=config_id, config_data=config, tenant_id=tenant_id)
    if db_config is None:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")
    return db_config

@router.delete("/tenant-configs/{config_id}", response_model=schemas.TenantConfig, tags=["Tenant Configurations"])
async def delete_tenant_config(config_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: SystemUser = Depends(get_current_active_user)):
    tenant_id = current_user.default_tenant_id
    db_config = await crud.delete_tenant_config(db, config_id=config_id, tenant_id=tenant_id)
    if db_config is None:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")
    return db_config
