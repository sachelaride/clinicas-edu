from sqlalchemy.ext.asyncio import AsyncSession # Changed from Session
from sqlalchemy import select, update, delete # Added imports
from typing import List, Optional
from uuid import UUID

from app.models.documentos_paciente import DocumentoPaciente
from app.schemas.documento_paciente import DocumentoPacienteCreate, DocumentoPacienteUpdate

async def get_documento_paciente(db: AsyncSession, documento_id: UUID) -> Optional[DocumentoPaciente]:
    result = await db.execute(select(DocumentoPaciente).filter(DocumentoPaciente.id == documento_id))
    return result.scalars().first()

async def get_documentos_paciente_by_paciente(db: AsyncSession, paciente_id: UUID, skip: int = 0, limit: int = 100) -> List[DocumentoPaciente]:
    result = await db.execute(
        select(DocumentoPaciente)
        .filter(DocumentoPaciente.paciente_id == paciente_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def create_documento_paciente(db: AsyncSession, documento: DocumentoPacienteCreate) -> DocumentoPaciente:
    db_documento = DocumentoPaciente(**documento.dict())
    db.add(db_documento)
    await db.commit()
    await db.refresh(db_documento)
    return db_documento

async def update_documento_paciente(db: AsyncSession, documento_id: UUID, documento: DocumentoPacienteUpdate) -> Optional[DocumentoPaciente]:
    stmt = update(DocumentoPaciente).where(DocumentoPaciente.id == documento_id).values(**documento.dict(exclude_unset=True))
    await db.execute(stmt)
    await db.commit()
    return await get_documento_paciente(db, documento_id) # Fetch updated object

async def delete_documento_paciente(db: AsyncSession, documento_id: UUID) -> Optional[DocumentoPaciente]:
    db_documento = await get_documento_paciente(db, documento_id) # Fetch object before deleting
    if db_documento:
        await db.execute(delete(DocumentoPaciente).where(DocumentoPaciente.id == documento_id))
        await db.commit()
    return db_documento