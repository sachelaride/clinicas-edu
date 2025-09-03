
from pydantic import BaseModel, UUID4
import datetime
from typing import Optional, List
from ..models.planos_custo import PlanoCustoStatus
from .planos_custo_itens import PlanoCustoItem

class PlanoCustoBase(BaseModel):
    paciente_id: UUID4
    tratamento_id: Optional[UUID4] = None
    status: PlanoCustoStatus = PlanoCustoStatus.pendente

class PlanoCustoCreate(PlanoCustoBase):
    pass

class PlanoCustoUpdate(BaseModel):
    status: Optional[PlanoCustoStatus] = None

class PlanoCusto(PlanoCustoBase):
    id: UUID4
    tenant_id: UUID4
    valor_total: float
    created_at: datetime.datetime
    updated_at: datetime.datetime
    itens: List[PlanoCustoItem] = []

    class Config:
        from_attributes = True
