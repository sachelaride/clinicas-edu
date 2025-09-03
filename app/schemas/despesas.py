
from pydantic import BaseModel
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

class DespesaBase(BaseModel):
    descricao: str
    valor: Decimal
    categoria: Optional[str] = None
    data_despesa: Optional[datetime] = None

class DespesaCreate(DespesaBase):
    pass

class DespesaUpdate(BaseModel):
    descricao: Optional[str] = None
    valor: Optional[Decimal] = None
    categoria: Optional[str] = None
    data_despesa: Optional[datetime] = None

class Despesa(DespesaBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
