from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid
import os
import shutil

from ..crud import consentimentos_paciente as crud
from ..schemas import consentimentos_paciente as schemas
from ..db.database import get_db
from ..routes.auth import get_current_active_user
from ..models.users import SystemUser
from ..core.permissions import can_manage_consent
from ..core.storage import get_storage_path
from fastapi.responses import FileResponse

router = APIRouter()

@router.post("/consentimentos/", response_model=schemas.ConsentimentoPaciente, status_code=status.HTTP_201_CREATED, tags=["Consentimentos Paciente"])
async def create_consentimento(
    paciente_id: uuid.UUID = Form(...),
    tipo_consentimento: str = Form(...),
    arquivo: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_manage_consent)
):
    tenant_id = current_user.default_tenant_id
    # Create the record without the file URL first to get an ID
    consentimento_data = schemas.ConsentimentoPacienteCreate(
        paciente_id=paciente_id,
        tipo_consentimento=tipo_consentimento,
        arquivo_url=""  # Placeholder
    )
    db_consentimento = await crud.create_consentimento(db=db, consentimento=consentimento_data, tenant_id=tenant_id)

    # Get the storage path
    file_extension = os.path.splitext(arquivo.filename)[1]
    file_path = get_storage_path(str(tenant_id), "consentimentos", str(db_consentimento.id), file_extension)

    # Save the file
    try:
        with open(file_path, "wb+") as file_object:
            shutil.copyfileobj(arquivo.file, file_object)
    except Exception as e:
        # If file saving fails, delete the created record
        await crud.delete_consentimento(db, consentimento_id=db_consentimento.id, tenant_id=tenant_id)
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")


    # Update the record with the file URL
    return await crud.update_consentimento_arquivo_url(db, consentimento_id=db_consentimento.id, arquivo_url=file_path, tenant_id=tenant_id)

@router.get("/consentimentos/", response_model=List[schemas.ConsentimentoPaciente], tags=["Consentimentos Paciente"])
async def read_consentimentos(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), current_user: SystemUser = Depends(can_manage_consent)):
    tenant_id = current_user.default_tenant_id
    return await crud.get_consentimentos(db, tenant_id=tenant_id, skip=skip, limit=limit)

@router.get("/consentimentos/{consentimento_id}", response_model=schemas.ConsentimentoPaciente, tags=["Consentimentos Paciente"])
async def read_consentimento(
    consentimento_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_manage_consent)
):
    tenant_id = current_user.default_tenant_id
    db_consentimento = await crud.get_consentimento(db, consentimento_id=consentimento_id, tenant_id=tenant_id)
    if db_consentimento is None:
        raise HTTPException(status_code=404, detail="Consentimento não encontrado")
    return db_consentimento

@router.put("/consentimentos/{consentimento_id}", response_model=schemas.ConsentimentoPaciente, tags=["Consentimentos Paciente"])
async def update_consentimento(
    consentimento_id: uuid.UUID,
    tipo_consentimento: Optional[str] = Form(None),
    arquivo: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_manage_consent)
):
    tenant_id = current_user.default_tenant_id
    update_data = {}
    if tipo_consentimento is not None:
        update_data["tipo_consentimento"] = tipo_consentimento
    
    if arquivo:
        file_extension = os.path.splitext(arquivo.filename)[1]
        file_path = get_storage_path(str(tenant_id), "consentimentos", str(consentimento_id), file_extension)
        
        # Save the new file
        try:
            with open(file_path, "wb+") as file_object:
                shutil.copyfileobj(arquivo.file, file_object)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
            
        update_data["arquivo_url"] = file_path
    
    consentimento_update = schemas.ConsentimentoPacienteUpdate(**update_data)
    db_consentimento = await crud.update_consentimento(db, consentimento_id=consentimento_id, consentimento_data=consentimento_update, tenant_id=tenant_id)
    
    if db_consentimento is None:
        raise HTTPException(status_code=404, detail="Consentimento não encontrado")
    return db_consentimento

@router.delete("/consentimentos/{consentimento_id}", response_model=schemas.ConsentimentoPaciente, tags=["Consentimentos Paciente"])
async def delete_consentimento(
    consentimento_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_manage_consent)
):
    tenant_id = current_user.default_tenant_id
    db_consentimento = await crud.delete_consentimento(db, consentimento_id=consentimento_id, tenant_id=tenant_id)
    if db_consentimento is None:
        raise HTTPException(status_code=404, detail="Consentimento não encontrado")
    # Note: This does not delete the file from storage. A background task could handle this.
    return db_consentimento

@router.get("/consentimentos/files/{consentimento_id}", tags=["Consentimentos Paciente"])
async def get_consentimento_file(consentimento_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: SystemUser = Depends(can_manage_consent)):
    tenant_id = current_user.default_tenant_id
    db_consentimento = await crud.get_consentimento(db, consentimento_id=consentimento_id, tenant_id=tenant_id)
    if not db_consentimento or not db_consentimento.arquivo_url:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    
    file_path = db_consentimento.arquivo_url
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado no sistema de arquivos")
        
    return FileResponse(file_path)

@router.get("/consentimentos/paciente/{paciente_id}", response_model=List[schemas.ConsentimentoPaciente], tags=["Consentimentos Paciente"])
async def get_consentimentos_by_paciente(paciente_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: SystemUser = Depends(can_manage_consent)):
    tenant_id = current_user.default_tenant_id
    return await crud.get_consentimentos_by_paciente(db, paciente_id=paciente_id, tenant_id=tenant_id)

