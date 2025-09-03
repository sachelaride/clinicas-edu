from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid
from datetime import date

from ..crud import pacientes as pacientes_crud
from ..schemas import pacientes as pacientes_schemas
from ..db.database import get_db
from ..routes.auth import get_current_active_user
from ..models.users import SystemUser, UserRole
from ..core.permissions import can_create_patient, can_read_patient, can_update_patient, can_delete_patient

router = APIRouter()

@router.post("/", response_model=pacientes_schemas.Paciente, status_code=status.HTTP_201_CREATED, tags=["Pacientes"])
async def create_paciente(
    paciente: pacientes_schemas.PacienteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_create_patient)
):
    print(f"Creating paciente with data: {paciente.dict()}")
    tenant_id = current_user.default_tenant_id

    today = date.today()
    age = today.year - paciente.data_nascimento.year - ((today.month, today.day) < (paciente.data_nascimento.month, paciente.data_nascimento.day))

    if age < 18:
        if not paciente.responsavel_id:
            raise HTTPException(
                status_code=400,
                detail="Para pacientes menores de 18 anos, o responsável é obrigatório.",
            )

    return await pacientes_crud.create_paciente(db=db, paciente=paciente, tenant_id=tenant_id)

@router.get("/{paciente_id}", response_model=pacientes_schemas.Paciente, tags=["Pacientes"])
async def read_paciente(
    paciente_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_read_patient)
):
    tenant_id = current_user.default_tenant_id
    if current_user.role == UserRole.admin_global:
        tenant_id = None # Admin global can read across all tenants

    db_paciente = await pacientes_crud.get_paciente(db, paciente_id=paciente_id, tenant_id=tenant_id)
    if db_paciente is None:
        raise HTTPException(status_code=404, detail="Paciente not found")
    return db_paciente

@router.get("/", response_model=List[pacientes_schemas.Paciente], tags=["Pacientes"])
async def read_pacientes(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_read_patient)
):
    tenant_id = current_user.default_tenant_id
    if current_user.role == UserRole.admin_global:
        pacientes = await pacientes_crud.get_pacientes(db, tenant_id=None, skip=skip, limit=limit)
    else:
        pacientes = await pacientes_crud.get_pacientes(db, tenant_id=tenant_id, skip=skip, limit=limit)
    
    return pacientes

@router.put("/{paciente_id}", response_model=pacientes_schemas.Paciente, tags=["Pacientes"])
async def update_paciente(
    paciente_id: uuid.UUID, 
    paciente: pacientes_schemas.PacienteUpdate, 
    db: AsyncSession = Depends(get_db), 
    current_user: SystemUser = Depends(can_update_patient)
):
    tenant_id = current_user.default_tenant_id
    db_paciente = await pacientes_crud.update_paciente(db, paciente_id=paciente_id, paciente_data=paciente, tenant_id=tenant_id)
    if db_paciente is None:
        raise HTTPException(status_code=404, detail="Paciente not found")
    return db_paciente

@router.delete("/{paciente_id}", response_model=pacientes_schemas.Paciente, tags=["Pacientes"])
async def delete_paciente(
    paciente_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user: SystemUser = Depends(can_delete_patient)
):
    tenant_id = current_user.default_tenant_id
    db_paciente = await pacientes_crud.delete_paciente(db, paciente_id=paciente_id, tenant_id=tenant_id)
    if db_paciente is None:
        raise HTTPException(status_code=404, detail="Paciente not found")
    return
