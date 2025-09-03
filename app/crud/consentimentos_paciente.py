
import uuid
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models import consentimentos_paciente as models
from ..schemas import consentimentos_paciente as schemas

async def get_consentimento(db: AsyncSession, consentimento_id: uuid.UUID, tenant_id: uuid.UUID):
    result = await db.execute(select(models.ConsentimentoPaciente).filter_by(id=consentimento_id, tenant_id=tenant_id))
    return result.scalars().first()

async def get_consentimentos(db: AsyncSession, tenant_id: uuid.UUID, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.ConsentimentoPaciente).filter_by(tenant_id=tenant_id).offset(skip).limit(limit))
    return result.scalars().all()

async def get_consentimentos_by_paciente(db: AsyncSession, paciente_id: uuid.UUID, tenant_id: uuid.UUID, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(models.ConsentimentoPaciente)
        .filter_by(paciente_id=paciente_id, tenant_id=tenant_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def create_consentimento(db: AsyncSession, consentimento: schemas.ConsentimentoPacienteCreate, tenant_id: uuid.UUID):
    db_consentimento = models.ConsentimentoPaciente(
        **consentimento.model_dump(),
        tenant_id=tenant_id
    )
    db.add(db_consentimento)
    await db.commit()
    await db.refresh(db_consentimento)
    return db_consentimento

async def update_consentimento(db: AsyncSession, consentimento_id: uuid.UUID, consentimento_data: schemas.ConsentimentoPacienteUpdate, tenant_id: uuid.UUID):
    result = await db.execute(select(models.ConsentimentoPaciente).filter_by(id=consentimento_id, tenant_id=tenant_id))
    db_consentimento = result.scalars().first()
    if db_consentimento:
        update_data = consentimento_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_consentimento, key, value)
        await db.commit()
        await db.refresh(db_consentimento)
    return db_consentimento

async def delete_consentimento(db: AsyncSession, consentimento_id: uuid.UUID, tenant_id: uuid.UUID):
    result = await db.execute(select(models.ConsentimentoPaciente).filter_by(id=consentimento_id, tenant_id=tenant_id))
    db_consentimento = result.scalars().first()
    if db_consentimento:
        # Delete the file from storage if it exists
        if db_consentimento.arquivo_url and os.path.exists(db_consentimento.arquivo_url):
            os.remove(db_consentimento.arquivo_url)
        
        await db.delete(db_consentimento)
        await db.commit()
    return db_consentimento

async def update_consentimento_arquivo_url(db: AsyncSession, consentimento_id: uuid.UUID, arquivo_url: str, tenant_id: uuid.UUID):
    """
    Atualiza a URL do arquivo de um consentimento existente.
    """
    db_consentimento = await get_consentimento(db, consentimento_id=consentimento_id, tenant_id=tenant_id)
    if db_consentimento:
        db_consentimento.arquivo_url = arquivo_url
        await db.commit()
        await db.refresh(db_consentimento)
    return db_consentimento
