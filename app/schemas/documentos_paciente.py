import uuid
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DocumentoPacienteBase(BaseModel):
    paciente_id: uuid.UUID
    nome_arquivo: str
    caminho_arquivo: str
    tipo_documento: Optional[str] = None

class DocumentoPacienteCreate(DocumentoPacienteBase):
    pass

class DocumentoPacienteUpdate(BaseModel):
    tipo: Optional[str] = None

class DocumentoPaciente(DocumentoPacienteBase):
    id: uuid.UUID
    paciente_id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
