from pydantic import BaseModel, UUID4
import datetime
from typing import Optional
from decimal import Decimal

class ServicoBase(BaseModel):
    nome: str
    valor: Decimal
    descricao: Optional[str] = None

class ServicoCreate(ServicoBase):
    pass

class ServicoUpdate(ServicoBase):
    nome: Optional[str] = None
    valor: Optional[Decimal] = None

class Servico(ServicoBase):
    id: UUID4
    tenant_id: UUID4
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True
