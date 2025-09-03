import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import Optional # Import Optional
from ..models import pacientes as models
from ..schemas import pacientes as schemas

async def get_paciente(db: AsyncSession, paciente_id: uuid.UUID, tenant_id: Optional[uuid.UUID]):
    stmt = select(models.Paciente).filter(models.Paciente.id == paciente_id)
    if tenant_id:
        stmt = stmt.filter(models.Paciente.tenant_id == tenant_id)
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_pacientes(db: AsyncSession, tenant_id: Optional[uuid.UUID], skip: int = 0, limit: int = 100):
    stmt = select(models.Paciente)
    if tenant_id is not None:
        stmt = stmt.filter(models.Paciente.tenant_id == tenant_id)
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    return result.scalars().all()

async def create_paciente(db: AsyncSession, paciente: schemas.PacienteCreate, tenant_id: uuid.UUID):
    paciente_data = paciente.model_dump(exclude_unset=True)
    if 'tenant_id' in paciente_data:
        del paciente_data['tenant_id']

    # Generate unique client_code
    # Get the count of existing patients for the tenant
    count_stmt = select(func.count()).filter(models.Paciente.tenant_id == tenant_id)
    total_patients = (await db.execute(count_stmt)).scalar_one()
    
    # Format the client_code (e.g., CLI-00001, CLI-00002)
    # Add 1 to the count because it's a new patient
    generated_client_code = f"CLI-{total_patients + 1:05d}"
    
    # Check for uniqueness (though unlikely with a sequential number, good practice)
    existing_client_code_stmt = select(models.Paciente).filter(
        models.Paciente.client_code == generated_client_code,
        models.Paciente.tenant_id == tenant_id
    )
    existing_paciente = (await db.execute(existing_client_code_stmt)).scalars().first()
    if existing_paciente:
        # Handle collision, e.g., by incrementing until unique or raising an error
        # For simplicity, I'll just increment for now. In a real app, more robust handling might be needed.
        i = 1
        while existing_paciente:
            generated_client_code = f"CLI-{total_patients + 1 + i:05d}"
            existing_client_code_stmt = select(models.Paciente).filter(
                models.Paciente.client_code == generated_client_code,
                models.Paciente.tenant_id == tenant_id
            )
            existing_paciente = (await db.execute(existing_client_code_stmt)).scalars().first()
            i += 1

    db_paciente = models.Paciente(
        **paciente_data,
        tenant_id=tenant_id,
        client_code=generated_client_code # Assign the generated client_code
    )
    db.add(db_paciente)
    await db.commit()
    await db.refresh(db_paciente)
    return db_paciente

async def update_paciente(db: AsyncSession, paciente_id: uuid.UUID, paciente_data: schemas.PacienteUpdate, tenant_id: uuid.UUID):
    result = await db.execute(select(models.Paciente).filter(models.Paciente.id == paciente_id, models.Paciente.tenant_id == tenant_id))
    db_paciente = result.scalars().first()
    if db_paciente:
        update_data = paciente_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_paciente, key, value)
        
        await db.commit()
        await db.refresh(db_paciente)
    return db_paciente

async def delete_paciente(db: AsyncSession, paciente_id: uuid.UUID, tenant_id: uuid.UUID):
    result = await db.execute(select(models.Paciente).filter(models.Paciente.id == paciente_id, models.Paciente.tenant_id == tenant_id))
    db_paciente = result.scalars().first()
    if db_paciente:
        await db.delete(db_paciente)
        await db.commit()
    return db_paciente
