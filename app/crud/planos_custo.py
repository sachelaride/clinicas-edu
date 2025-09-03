
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from ..models import planos_custo as models, planos_custo_itens as item_models, servicos as servico_models
from ..schemas import planos_custo as schemas, planos_custo_itens as item_schemas

async def get_plano_custo(db: AsyncSession, plano_custo_id: uuid.UUID, tenant_id: uuid.UUID):
    result = await db.execute(
        select(models.PlanoCusto)
        .options(selectinload(models.PlanoCusto.itens))
        .filter(models.PlanoCusto.id == plano_custo_id, models.PlanoCusto.tenant_id == tenant_id)
    )
    return result.scalars().first()

async def get_planos_custo(db: AsyncSession, tenant_id: uuid.UUID, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(models.PlanoCusto)
        .filter(models.PlanoCusto.tenant_id == tenant_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def create_plano_custo(db: AsyncSession, plano_custo: schemas.PlanoCustoCreate, tenant_id: uuid.UUID):
    db_plano_custo = models.PlanoCusto(
        paciente_id=plano_custo.paciente_id,
        tratamento_id=plano_custo.tratamento_id,
        status=plano_custo.status,
        tenant_id=tenant_id,
        valor_total=0  # Initial value
    )
    db.add(db_plano_custo)
    await db.commit()
    await db.refresh(db_plano_custo)
    return db_plano_custo

async def update_plano_custo(db: AsyncSession, plano_custo_id: uuid.UUID, plano_custo_data: schemas.PlanoCustoUpdate, tenant_id: uuid.UUID):
    result = await db.execute(select(models.PlanoCusto).filter_by(id=plano_custo_id, tenant_id=tenant_id))
    db_plano_custo = result.scalars().first()
    if db_plano_custo:
        update_data = plano_custo_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_plano_custo, key, value)
        await db.commit()
        await db.refresh(db_plano_custo)
    return db_plano_custo

async def delete_plano_custo(db: AsyncSession, plano_custo_id: uuid.UUID, tenant_id: uuid.UUID):
    result = await db.execute(select(models.PlanoCusto).filter_by(id=plano_custo_id, tenant_id=tenant_id))
    db_plano_custo = result.scalars().first()
    if db_plano_custo:
        await db.delete(db_plano_custo)
        await db.commit()
    return db_plano_custo

async def _recalculate_valor_total(db: AsyncSession, plano_custo_id: uuid.UUID):
    result = await db.execute(
        select(item_models.PlanoCustoItem).filter_by(plano_custo_id=plano_custo_id)
    )
    itens = result.scalars().all()
    valor_total = sum(item.valor * item.quantidade for item in itens)
    
    plano_result = await db.execute(select(models.PlanoCusto).filter_by(id=plano_custo_id))
    db_plano_custo = plano_result.scalars().first()
    if db_plano_custo:
        db_plano_custo.valor_total = valor_total
        await db.commit()

async def add_item_to_plano_custo(db: AsyncSession, plano_custo_id: uuid.UUID, item: item_schemas.PlanoCustoItemCreate, tenant_id: uuid.UUID):
    # Check if plano_custo exists and belongs to the tenant
    plano_result = await db.execute(select(models.PlanoCusto).filter_by(id=plano_custo_id, tenant_id=tenant_id))
    if not plano_result.scalars().first():
        return None

    # Get service value
    servico_result = await db.execute(select(servico_models.Servico).filter_by(id=item.servico_id, tenant_id=tenant_id))
    servico = servico_result.scalars().first()
    if not servico:
        return None # Or raise exception

    db_item = item_models.PlanoCustoItem(
        plano_custo_id=plano_custo_id,
        servico_id=item.servico_id,
        quantidade=item.quantidade,
        valor=servico.valor, # Use the value from the servicos table
        tenant_id=tenant_id
    )
    db.add(db_item)
    await db.commit()
    await _recalculate_valor_total(db, plano_custo_id)
    await db.refresh(db_item)
    return db_item

async def remove_item_from_plano_custo(db: AsyncSession, plano_custo_id: uuid.UUID, item_id: uuid.UUID, tenant_id: uuid.UUID):
    result = await db.execute(
        select(item_models.PlanoCustoItem).filter_by(id=item_id, plano_custo_id=plano_custo_id, tenant_id=tenant_id)
    )
    db_item = result.scalars().first()
    if db_item:
        await db.delete(db_item)
        await db.commit()
        await _recalculate_valor_total(db, plano_custo_id)
    return db_item
