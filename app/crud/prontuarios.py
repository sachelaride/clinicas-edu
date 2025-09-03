from sqlalchemy.ext.asyncio import AsyncSession # Changed from Session
from sqlalchemy import select, update, delete # Added imports
from typing import List, Optional
from uuid import UUID

from app.models.prontuarios import Prontuario
from app.schemas.prontuario import ProntuarioCreate, ProntuarioUpdate

async def get_prontuario(db: AsyncSession, prontuario_id: UUID) -> Optional[Prontuario]:
    result = await db.execute(select(Prontuario).filter(Prontuario.id == prontuario_id))
    return result.scalars().first()

async def get_prontuarios_by_paciente(db: AsyncSession, paciente_id: UUID, skip: int = 0, limit: int = 100) -> List[Prontuario]:
    result = await db.execute(
        select(Prontuario)
        .filter(Prontuario.paciente_id == paciente_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def create_prontuario(db: AsyncSession, prontuario: ProntuarioCreate) -> Prontuario:
    db_prontuario = Prontuario(**prontuario.dict())
    db.add(db_prontuario)
    await db.commit()
    await db.refresh(db_prontuario)
    return db_prontuario

async def update_prontuario(db: AsyncSession, prontuario_id: UUID, prontuario: ProntuarioUpdate) -> Optional[Prontuario]:
    stmt = update(Prontuario).where(Prontuario.id == prontuario_id).values(**prontuario.dict(exclude_unset=True))
    await db.execute(stmt)
    await db.commit()
    return await get_prontuario(db, prontuario_id) # Fetch updated object

async def delete_prontuario(db: AsyncSession, prontuario_id: UUID) -> Optional[Prontuario]:
    db_prontuario = await get_prontuario(db, prontuario_id) # Fetch object before deleting
    if db_prontuario:
        await db.execute(delete(Prontuario).where(Prontuario.id == prontuario_id))
        await db.commit()
    return db_prontuario