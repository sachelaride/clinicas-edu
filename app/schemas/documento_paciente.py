from pydantic import BaseModel, Field
from typing import Optional
import uuid
from datetime import datetime

class DocumentoPacienteBase(BaseModel):
    paciente_id: uuid.UUID
    nome_arquivo: str = Field(..., max_length=255)
    caminho_arquivo: str = Field(..., max_length=512)
    tipo_documento: Optional[str] = Field(None, max_length=100)

class DocumentoPacienteCreate(DocumentoPacienteBase):
    pass

class DocumentoPacienteUpdate(DocumentoPacienteBase):
    pass

class DocumentoPacienteInDB(DocumentoPacienteBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True