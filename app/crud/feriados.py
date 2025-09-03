import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from ..models import feriados as models
from ..schemas import feriados as schemas

async def get_feriado(db: AsyncSession, feriado_id: uuid.UUID, tenant_id: uuid.UUID):
    result = await db.execute(select(models.Feriado).filter_by(id=feriado_id, tenant_id=tenant_id))
    return result.scalars().first()

async def get_feriados(db: AsyncSession, tenant_id: uuid.UUID, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Feriado).filter_by(tenant_id=tenant_id).offset(skip).limit(limit))
    return result.scalars().all()

async def create_feriado(db: AsyncSession, feriado: schemas.FeriadoCreate, tenant_id: uuid.UUID):
    existing_feriado = await db.execute(
        select(models.Feriado).filter_by(data=feriado.data, tenant_id=tenant_id)
    )
    if existing_feriado.scalars().first():
        raise HTTPException(status_code=409, detail="Feriado nesta data já existe para este tenant.")

    db_feriado = models.Feriado(
        **feriado.model_dump(),
        tenant_id=tenant_id
    )
    db.add(db_feriado)
    await db.commit()
    await db.refresh(db_feriado)
    return db_feriado

async def update_feriado(db: AsyncSession, feriado_id: uuid.UUID, feriado_data: schemas.FeriadoUpdate, tenant_id: uuid.UUID):
    result = await db.execute(select(models.Feriado).filter_by(id=feriado_id, tenant_id=tenant_id))
    db_feriado = result.scalars().first()
    if db_feriado:
        update_data = feriado_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_feriado, key, value)
        await db.commit()
        await db.refresh(db_feriado)
    return db_feriado

async def delete_feriado(db: AsyncSession, feriado_id: uuid.UUID, tenant_id: uuid.UUID):
    result = await db.execute(select(models.Feriado).filter_by(id=feriado_id, tenant_id=tenant_id))
    db_feriado = result.scalars().first()
    if db_feriado:
        await db.delete(db_feriado)
        await db.commit()
    return db_feriado
