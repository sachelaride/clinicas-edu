from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid
import os # Keep os for path manipulation if needed, but mostly replaced by pathlib
# from pathlib import Path # Not directly used in the new logic, but Path is used in FileStorageService
# import shutil # Not needed anymore

from app.schemas.documento_paciente import DocumentoPacienteCreate, DocumentoPacienteUpdate, DocumentoPacienteInDB
from app.crud import documentos_paciente as crud_documentos_paciente
from app.db.database import get_db
from app.routes.auth import get_current_active_user
from app.services.file_storage_service import file_storage_service # Import the service
# from app.core.storage import get_storage_path # Not needed anymore
from fastapi.responses import FileResponse
from app.models.users import SystemUser, UserRole
from app.crud import tenants as crud_tenants # Import tenants_crud

router = APIRouter()

@router.post("/", response_model=DocumentoPacienteInDB, status_code=status.HTTP_201_CREATED, tags=["Documentos Paciente"])
async def create_documento_paciente(
    paciente_id: uuid.UUID = Form(...),
    tipo_documento: str = Form(...), # Changed from 'tipo' to 'tipo_documento' to match schema
    file: UploadFile = File(...), # Changed from 'arquivo' to 'file'
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(get_current_active_user)
):
    tenant_id = current_user.default_tenant_id
    tenant = await crud_tenants.get_tenant(db, tenant_id=tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    clinic_name = tenant.nome

    file_content = await file.read()
    file_extension = os.path.splitext(file.filename)[1].lstrip('.') # Get extension without dot

    try:
        caminho_arquivo = file_storage_service.save_documento_file(clinic_name, file_content, file_extension)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    documento_create = DocumentoPacienteCreate(
        paciente_id=paciente_id,
        nome_arquivo=file.filename,
        caminho_arquivo=caminho_arquivo,
        tipo_documento=tipo_documento
    )
    return await crud_documentos_paciente.create_documento_paciente(db=db, documento=documento_create)

@router.get("/paciente/{paciente_id}", response_model=List[DocumentoPacienteInDB], tags=["Documentos Paciente"])
async def read_documentos_paciente(
    paciente_id: uuid.UUID, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(get_current_active_user)
):
    # Tenant filtering logic for admin_global should be handled in CRUD or by fetching patient's tenant
    # For now, assuming crud.get_documentos_paciente_by_paciente handles tenant context if needed
    return await crud_documentos_paciente.get_documentos_paciente_by_paciente(db, paciente_id=paciente_id, skip=skip, limit=limit)

@router.get("/{documento_id}/file", tags=["Documentos Paciente"])
async def get_documento_paciente_file(documento_id: uuid.UUID, db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(get_current_active_user)
):
    db_documento = await crud_documentos_paciente.get_documento_paciente(db, documento_id=documento_id)
    if not db_documento or not db_documento.caminho_arquivo:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    
    full_file_path = file_storage_service.base_upload_dir / db_documento.caminho_arquivo
    if not full_file_path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado no sistema de arquivos")
        
    return FileResponse(full_file_path)

@router.delete("/{documento_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Documentos Paciente"])
async def delete_documento_paciente(
    documento_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(get_current_active_user)
):
    if current_user.role not in [UserRole.admin_global, UserRole.gestor_clinica]:
        raise HTTPException(status_code=403, detail="Not authorized to delete documents")

    db_documento = await crud_documentos_paciente.get_documento_paciente(db, documento_id=documento_id)
    if db_documento is None:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    
    # Delete file from storage
    try:
        file_storage_service.delete_file(db_documento.caminho_arquivo)
    except Exception as e:
        print(f"WARNING: Failed to delete file {db_documento.caminho_arquivo} from storage: {e}")
        # Optionally, raise HTTPException or log more severely

    # Delete record from database
    await crud_documentos_paciente.delete_documento_paciente(db, documento_id=documento_id)
    
    return {"message": "Documento deleted successfully"}
