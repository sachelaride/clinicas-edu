
import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models import pagamentos as models
from ..schemas import pagamentos as schemas

async def get_pagamento(db: AsyncSession, pagamento_id: uuid.UUID, tenant_id: uuid.UUID) -> Optional[models.Pagamento]:
    result = await db.execute(
        select(models.Pagamento).filter(models.Pagamento.id == pagamento_id, models.Pagamento.tenant_id == tenant_id)
    )
    return result.scalars().first()

async def get_pagamentos_by_paciente(db: AsyncSession, paciente_id: uuid.UUID, tenant_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[models.Pagamento]:
    result = await db.execute(
        select(models.Pagamento)
        .filter(models.Pagamento.paciente_id == paciente_id, models.Pagamento.tenant_id == tenant_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def create_pagamento(db: AsyncSession, pagamento: schemas.PagamentoCreate, tenant_id: uuid.UUID) -> models.Pagamento:
    db_pagamento = models.Pagamento(
        **pagamento.model_dump(),
        tenant_id=tenant_id
    )
    db.add(db_pagamento)
    await db.commit()
    await db.refresh(db_pagamento)
    return db_pagamento

async def update_pagamento(db: AsyncSession, pagamento_id: uuid.UUID, pagamento_data: schemas.PagamentoUpdate, tenant_id: uuid.UUID) -> Optional[models.Pagamento]:
    db_pagamento = await get_pagamento(db, pagamento_id=pagamento_id, tenant_id=tenant_id)
    if db_pagamento:
        update_data = pagamento_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_pagamento, key, value)
        await db.commit()
        await db.refresh(db_pagamento)
    return db_pagamento

async def delete_pagamento(db: AsyncSession, pagamento_id: uuid.UUID, tenant_id: uuid.UUID) -> Optional[models.Pagamento]:
    db_pagamento = await get_pagamento(db, pagamento_id=pagamento_id, tenant_id=tenant_id)
    if db_pagamento:
        await db.delete(db_pagamento)
        await db.commit()
    return db_pagamento
