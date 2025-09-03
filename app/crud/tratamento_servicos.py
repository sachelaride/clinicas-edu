import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from ..models import tratamento_servicos as models
from ..models import tratamentos as tratamento_models
from ..schemas import tratamento_servicos as schemas

async def add_servico_to_tratamento(db: AsyncSession, tratamento_id: uuid.UUID, servico_id: uuid.UUID, quantidade: int, tenant_id: uuid.UUID, academico_id: uuid.UUID = None, monitor_id: uuid.UUID = None):
    # First, ensure the treatment exists and belongs to the tenant
    tratamento_result = await db.execute(
        select(tratamento_models.Tratamento).filter_by(id=tratamento_id, tenant_id=tenant_id)
    )
    if not tratamento_result.scalars().first():
        return None # Or raise an exception

    db_tratamento_servico = models.TratamentoServico(
        tratamento_id=tratamento_id,
        servico_id=servico_id,
        quantidade=quantidade,
        tenant_id=tenant_id,
        academico_id=academico_id,
        monitor_id=monitor_id
    )
    db.add(db_tratamento_servico)
    return db_tratamento_servico

async def remove_servico_from_tratamento(db: AsyncSession, tratamento_id: uuid.UUID, servico_id: uuid.UUID, tenant_id: uuid.UUID):
    result = await db.execute(
        select(models.TratamentoServico).filter_by(
            tratamento_id=tratamento_id, 
            servico_id=servico_id, 
            tenant_id=tenant_id
        )
    )
    db_tratamento_servico = result.scalars().first()
    if db_tratamento_servico:
        await db.delete(db_tratamento_servico)
    return db_tratamento_servico

async def get_servicos_for_tratamento(db: AsyncSession, tratamento_id: uuid.UUID, tenant_id: uuid.UUID):
    result = await db.execute(
        select(tratamento_models.Tratamento)
        .options(selectinload(tratamento_models.Tratamento.servicos))
        .filter_by(id=tratamento_id, tenant_id=tenant_id)
    )
    tratamento = result.scalars().first()
    return tratamento.servicos if tratamento else []