from pydantic import BaseModel, Field
from typing import Optional
import uuid
from datetime import datetime

class ProntuarioBase(BaseModel):
    paciente_id: uuid.UUID
    agendamento_id: Optional[uuid.UUID] = None
    servico_id: Optional[uuid.UUID] = None
    conteudo: str = Field(..., min_length=1)
    caminho_arquivo: Optional[str] = Field(None, max_length=512)

class ProntuarioCreate(ProntuarioBase):
    pass

class ProntuarioUpdate(ProntuarioBase):
    pass

class ProntuarioInDB(ProntuarioBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True