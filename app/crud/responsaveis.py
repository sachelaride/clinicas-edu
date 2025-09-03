from sqlalchemy.ext.asyncio import AsyncSession # Changed from Session
from sqlalchemy import select, update, delete # Added imports
from typing import List, Optional
from uuid import UUID

from app.models.responsaveis import Responsavel
from app.schemas.responsavel import ResponsavelCreate, ResponsavelUpdate

async def get_responsavel(db: AsyncSession, responsavel_id: UUID) -> Optional[Responsavel]:
    result = await db.execute(select(Responsavel).filter(Responsavel.id == responsavel_id))
    return result.scalars().first()

async def get_responsaveis(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Responsavel]:
    result = await db.execute(
        select(Responsavel)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def create_responsavel(db: AsyncSession, responsavel: ResponsavelCreate) -> Responsavel:
    print(f"Creating responsavel with data: {responsavel.dict()}")
    db_responsavel = Responsavel(**responsavel.dict())
    db.add(db_responsavel)
    await db.commit()
    await db.refresh(db_responsavel)
    return db_responsavel

async def update_responsavel(db: AsyncSession, responsavel_id: UUID, responsavel: ResponsavelUpdate) -> Optional[Responsavel]:
    stmt = update(Responsavel).where(Responsavel.id == responsavel_id).values(**responsavel.dict(exclude_unset=True))
    await db.execute(stmt)
    await db.commit()
    return await get_responsavel(db, responsavel_id) # Fetch updated object

async def delete_responsavel(db: AsyncSession, responsavel_id: UUID) -> Optional[Responsavel]:
    db_responsavel = await get_responsavel(db, responsavel_id) # Fetch object before deleting
    if db_responsavel:
        await db.execute(delete(Responsavel).where(Responsavel.id == responsavel_id))
        await db.commit()
    return db_responsavel