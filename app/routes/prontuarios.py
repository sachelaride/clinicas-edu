from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid
import os

from app.schemas.prontuario import ProntuarioCreate, ProntuarioUpdate, ProntuarioInDB
from app.crud import prontuarios as crud_prontuarios
from app.db.database import get_db
from app.routes.auth import get_current_active_user
from app.services.file_storage_service import file_storage_service
from fastapi.responses import FileResponse
from app.models.users import SystemUser, UserRole
from app.crud import tenants as crud_tenants

router = APIRouter()

@router.post("/", response_model=ProntuarioInDB, status_code=status.HTTP_201_CREATED, tags=["Prontuarios"])
async def create_prontuario(
    paciente_id: uuid.UUID = Form(...),
    conteudo: str = Form(...),
    agendamento_id: uuid.UUID = Form(None),
    servico_id: uuid.UUID = Form(None),
    file: UploadFile = File(...), # Prontuario content as a file
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(get_current_active_user)
):
    tenant_id = current_user.default_tenant_id
    tenant = await crud_tenants.get_tenant(db, tenant_id=tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    clinic_name = tenant.nome

    file_content = await file.read()
    file_extension = os.path.splitext(file.filename)[1].lstrip('.')

    try:
        caminho_arquivo = file_storage_service.save_prontuario_file(clinic_name, file_content, file_extension)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save prontuario file: {e}")

    prontuario_create = ProntuarioCreate(
        paciente_id=paciente_id,
        conteudo=conteudo,
        agendamento_id=agendamento_id,
        servico_id=servico_id,
        caminho_arquivo=caminho_arquivo # Now storing the file path
    )
    return await crud_prontuarios.create_prontuario(db=db, prontuario=prontuario_create)

@router.get("/paciente/{paciente_id}", response_model=List[ProntuarioInDB], tags=["Prontuarios"])
async def read_prontuarios_by_paciente(
    paciente_id: uuid.UUID, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(get_current_active_user)
):
    return await crud_prontuarios.get_prontuarios_by_paciente(db, paciente_id=paciente_id, skip=skip, limit=limit)

@router.get("/{prontuario_id}/file", tags=["Prontuarios"])
async def get_prontuario_file(prontuario_id: uuid.UUID, db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(get_current_active_user)
):
    db_prontuario = await crud_prontuarios.get_prontuario(db, prontuario_id=prontuario_id)
    if not db_prontuario or not db_prontuario.caminho_arquivo:
        raise HTTPException(status_code=404, detail="Arquivo de prontuário não encontrado")
    
    full_file_path = file_storage_service.base_upload_dir / db_prontuario.caminho_arquivo
    if not full_file_path.exists():
        raise HTTPException(status_code=404, detail="Arquivo de prontuário não encontrado no sistema de arquivos")
        
    return FileResponse(full_file_path)

@router.put("/{prontuario_id}", response_model=ProntuarioInDB, tags=["Prontuarios"])
async def update_prontuario(
    prontuario_id: uuid.UUID,
    prontuario: ProntuarioUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(get_current_active_user)
):
    if current_user.role not in [UserRole.admin_global, UserRole.gestor_clinica, UserRole.medico]:
        raise HTTPException(status_code=403, detail="Not authorized to update prontuarios")
    
    db_prontuario = await crud_prontuarios.update_prontuario(db=db, prontuario_id=prontuario_id, prontuario=prontuario)
    if db_prontuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prontuario not found")
    return db_prontuario

@router.delete("/{prontuario_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Prontuarios"])
async def delete_prontuario(
    prontuario_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(get_current_active_user)
):
    if current_user.role not in [UserRole.admin_global, UserRole.gestor_clinica, UserRole.medico]:
        raise HTTPException(status_code=403, detail="Not authorized to delete prontuarios")

    db_prontuario = await crud_prontuarios.get_prontuario(db, prontuario_id=prontuario_id)
    if db_prontuario is None:
        raise HTTPException(status_code=404, detail="Prontuario not found")
    
    # Delete file from storage
    if db_prontuario.caminho_arquivo:
        try:
            file_storage_service.delete_file(db_prontuario.caminho_arquivo)
        except Exception as e:
            print(f"WARNING: Failed to delete prontuario file {db_prontuario.caminho_arquivo} from storage: {e}")

    # Delete record from database
    await crud_prontuarios.delete_prontuario(db, prontuario_id=prontuario_id)
    
    return {"message": "Prontuario deleted successfully"}