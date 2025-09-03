
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models import tenant_configs as models
from ..schemas import tenant_configs as schemas

async def get_tenant_config(db: AsyncSession, config_id: uuid.UUID, tenant_id: uuid.UUID):
    result = await db.execute(select(models.TenantConfig).filter_by(id=config_id, tenant_id=tenant_id))
    return result.scalars().first()

async def get_tenant_configs(db: AsyncSession, tenant_id: uuid.UUID, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.TenantConfig).filter_by(tenant_id=tenant_id).offset(skip).limit(limit))
    return result.scalars().all()

async def create_tenant_config(db: AsyncSession, config: schemas.TenantConfigCreate, tenant_id: uuid.UUID):
    db_config = models.TenantConfig(
        **config.model_dump(),
        tenant_id=tenant_id
    )
    db.add(db_config)
    await db.commit()
    await db.refresh(db_config)
    return db_config

async def update_tenant_config(db: AsyncSession, config_id: uuid.UUID, config_data: schemas.TenantConfigUpdate, tenant_id: uuid.UUID):
    result = await db.execute(select(models.TenantConfig).filter_by(id=config_id, tenant_id=tenant_id))
    db_config = result.scalars().first()
    if db_config:
        update_data = config_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_config, key, value)
        await db.commit()
        await db.refresh(db_config)
    return db_config

async def delete_tenant_config(db: AsyncSession, config_id: uuid.UUID, tenant_id: uuid.UUID):
    result = await db.execute(select(models.TenantConfig).filter_by(id=config_id, tenant_id=tenant_id))
    db_config = result.scalars().first()
    if db_config:
        await db.delete(db_config)
        await db.commit()
    return db_config
