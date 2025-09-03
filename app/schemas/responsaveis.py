from pydantic import BaseModel, UUID4, EmailStr
import datetime
from typing import Optional

class ResponsavelBase(BaseModel):
    nome: str
    documento: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None

class ResponsavelCreate(ResponsavelBase):
    pass

class ResponsavelUpdate(ResponsavelBase):
    nome: Optional[str] = None

class Responsavel(ResponsavelBase):
    id: UUID4
    tenant_id: UUID4
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True