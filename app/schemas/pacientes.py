from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime
import uuid

class PacienteBase(BaseModel):
    nome: str
    data_nascimento: date
    genero: str
    endereco: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None
    responsavel_id: Optional[uuid.UUID] = None
    

class PacienteCreate(PacienteBase):
    pass

class PacienteUpdate(PacienteBase):
    pass

class Paciente(PacienteBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True