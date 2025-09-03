
import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models import despesas as models
from ..schemas import despesas as schemas

async def get_despesa(db: AsyncSession, despesa_id: uuid.UUID, tenant_id: uuid.UUID) -> Optional[models.Despesa]:
    result = await db.execute(
        select(models.Despesa).filter(models.Despesa.id == despesa_id, models.Despesa.tenant_id == tenant_id)
    )
    return result.scalars().first()

async def get_despesas(db: AsyncSession, tenant_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[models.Despesa]:
    result = await db.execute(
        select(models.Despesa)
        .filter(models.Despesa.tenant_id == tenant_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def create_despesa(db: AsyncSession, despesa: schemas.DespesaCreate, tenant_id: uuid.UUID) -> models.Despesa:
    db_despesa = models.Despesa(
        **despesa.model_dump(),
        tenant_id=tenant_id
    )
    db.add(db_despesa)
    await db.commit()
    await db.refresh(db_despesa)
    return db_despesa

async def update_despesa(db: AsyncSession, despesa_id: uuid.UUID, despesa_data: schemas.DespesaUpdate, tenant_id: uuid.UUID) -> Optional[models.Despesa]:
    db_despesa = await get_despesa(db, despesa_id=despesa_id, tenant_id=tenant_id)
    if db_despesa:
        update_data = despesa_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_despesa, key, value)
        await db.commit()
        await db.refresh(db_despesa)
    return db_despesa

async def delete_despesa(db: AsyncSession, despesa_id: uuid.UUID, tenant_id: uuid.UUID) -> Optional[models.Despesa]:
    db_despesa = await get_despesa(db, despesa_id=despesa_id, tenant_id=tenant_id)
    if db_despesa:
        await db.delete(db_despesa)
        await db.commit()
    return db_despesa
