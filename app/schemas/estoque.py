
from pydantic import BaseModel, UUID4
import datetime
from typing import Optional

class EstoqueBase(BaseModel):
    nome: str
    unidade: str
    quantidade: Optional[float] = 0
    min_quantidade: float

class EstoqueCreate(EstoqueBase):
    pass

class EstoqueUpdate(BaseModel):
    nome: Optional[str] = None
    unidade: Optional[str] = None
    min_quantidade: Optional[float] = None

class Estoque(EstoqueBase):
    id: UUID4
    tenant_id: UUID4
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True
