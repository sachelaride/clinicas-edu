from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from ..crud import tenants as tenants_crud
from ..schemas import tenants as tenants_schemas
from ..db.database import get_db
from ..routes.auth import get_current_active_user
from ..models.users import SystemUser, UserRole
from ..core.permissions import can_manage_tenants

router = APIRouter()

@router.post("/", response_model=tenants_schemas.Tenant, status_code=status.HTTP_201_CREATED, tags=["Tenants"])
async def create_tenant(
    tenant: tenants_schemas.TenantCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_manage_tenants)
):
    return await tenants_crud.create_tenant(db=db, tenant=tenant)

@router.get("/", response_model=List[tenants_schemas.Tenant], tags=["Tenants"])
async def read_tenants(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_manage_tenants)
):
    tenants = await tenants_crud.get_tenants(db, skip=skip, limit=limit)
    return tenants

@router.get("/{tenant_id}", response_model=tenants_schemas.Tenant, tags=["Tenants"])
async def read_tenant(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(get_current_active_user)
):
    if current_user.role != UserRole.admin_global and current_user.default_tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this tenant")
    db_tenant = await tenants_crud.get_tenant(db, tenant_id=tenant_id)
    if db_tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return db_tenant

@router.put("/{tenant_id}", response_model=tenants_schemas.Tenant, tags=["Tenants"])
async def update_tenant(
    tenant_id: uuid.UUID,
    tenant: tenants_schemas.TenantUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_manage_tenants)
):
    db_tenant = await tenants_crud.update_tenant(db, tenant_id=tenant_id, tenant_data=tenant)
    if db_tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return db_tenant

@router.delete("/{tenant_id}", response_model=tenants_schemas.Tenant, tags=["Tenants"])
async def delete_tenant(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_manage_tenants)
):
    db_tenant = await tenants_crud.delete_tenant(db, tenant_id=tenant_id)
    if db_tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return db_tenant
