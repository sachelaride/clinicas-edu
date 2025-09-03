
from pydantic import BaseModel, UUID4
import datetime
from typing import Optional

class ConsentimentoPacienteBase(BaseModel):
    paciente_id: UUID4
    tipo_consentimento: str
    arquivo_url: Optional[str] = None

class ConsentimentoPacienteCreate(BaseModel):
    paciente_id: UUID4
    tipo_consentimento: str

class ConsentimentoPacienteUpdate(BaseModel):
    tipo_consentimento: Optional[str] = None

class ConsentimentoPacienteUpload(ConsentimentoPacienteBase):
    arquivo_url: str

class ConsentimentoPaciente(ConsentimentoPacienteBase):
    id: UUID4
    tenant_id: UUID4
    data_consentimento: datetime.datetime
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True
