
from pydantic import BaseModel
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from ..models.pagamentos import MetodoPagamento

class PagamentoBase(BaseModel):
    valor: Decimal
    metodo_pagamento: MetodoPagamento
    data_pagamento: Optional[datetime] = None
    paciente_id: uuid.UUID
    plano_custo_id: Optional[uuid.UUID] = None
    observacoes: Optional[str] = None

class PagamentoCreate(PagamentoBase):
    pass

class PagamentoUpdate(BaseModel):
    valor: Optional[Decimal] = None
    metodo_pagamento: Optional[MetodoPagamento] = None
    data_pagamento: Optional[datetime] = None
    observacoes: Optional[str] = None

class Pagamento(PagamentoBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
