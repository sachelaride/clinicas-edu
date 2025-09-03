import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models import tenants as models
from ..schemas import tenants as schemas

async def get_tenant(db: AsyncSession, tenant_id: uuid.UUID):
    result = await db.execute(select(models.Tenant).filter(models.Tenant.id == tenant_id))
    return result.scalars().first()

async def get_tenants(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Tenant).offset(skip).limit(limit))
    return result.scalars().all()

async def create_tenant(db: AsyncSession, tenant: schemas.TenantCreate):
    db_tenant = models.Tenant(nome=tenant.nome, cnpj=tenant.cnpj)
    db.add(db_tenant)
    await db.commit()
    await db.refresh(db_tenant)
    return db_tenant

async def update_tenant(db: AsyncSession, tenant_id: uuid.UUID, tenant_data: schemas.TenantUpdate):
    result = await db.execute(select(models.Tenant).filter(models.Tenant.id == tenant_id))
    db_tenant = result.scalars().first()
    if db_tenant:
        update_data = tenant_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_tenant, key, value)
        await db.commit()
        await db.refresh(db_tenant)
    return db_tenant

async def delete_tenant(db: AsyncSession, tenant_id: uuid.UUID):
    result = await db.execute(select(models.Tenant).filter(models.Tenant.id == tenant_id))
    db_tenant = result.scalars().first()
    if db_tenant:
        await db.delete(db_tenant)
        await db.commit()
    return db_tenant
