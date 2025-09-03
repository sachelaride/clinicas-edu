import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models import servicos as models
from ..schemas import servicos as schemas

async def get_servico(db: AsyncSession, servico_id: uuid.UUID, tenant_id: uuid.UUID):
    result = await db.execute(select(models.Servico).filter(models.Servico.id == servico_id, models.Servico.tenant_id == tenant_id))
    return result.scalars().first()

from typing import Optional # Add this import

async def get_servicos(db: AsyncSession, tenant_id: Optional[uuid.UUID], skip: int = 0, limit: int = 100):
    stmt = select(models.Servico)
    if tenant_id is not None:
        stmt = stmt.filter(models.Servico.tenant_id == tenant_id)
    result = await db.execute(stmt.offset(skip).limit(limit))
    return result.scalars().all()

async def create_servico(db: AsyncSession, servico: schemas.ServicoCreate, tenant_id: uuid.UUID):
    db_servico = models.Servico(
        **servico.model_dump(),
        tenant_id=tenant_id
    )
    db.add(db_servico)
    await db.commit()
    await db.refresh(db_servico)
    return db_servico

async def update_servico(db: AsyncSession, servico_id: uuid.UUID, servico_data: schemas.ServicoUpdate, tenant_id: uuid.UUID):
    result = await db.execute(select(models.Servico).filter(models.Servico.id == servico_id, models.Servico.tenant_id == tenant_id))
    db_servico = result.scalars().first()
    if db_servico:
        update_data = servico_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_servico, key, value)
        
        await db.commit()
        await db.refresh(db_servico)
    return db_servico

async def delete_servico(db: AsyncSession, servico_id: uuid.UUID, tenant_id: uuid.UUID):
    result = await db.execute(select(models.Servico).filter(models.Servico.id == servico_id, models.Servico.tenant_id == tenant_id))
    db_servico = result.scalars().first()
    if db_servico:
        await db.delete(db_servico)
        await db.commit()
    return db_servico
