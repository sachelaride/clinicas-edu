
from pydantic import BaseModel, UUID4

class PlanoCustoItemBase(BaseModel):
    servico_id: UUID4
    quantidade: int = 1
    valor: float

class PlanoCustoItemCreate(PlanoCustoItemBase):
    pass

class PlanoCustoItem(PlanoCustoItemBase):
    id: UUID4
    plano_custo_id: UUID4
    tenant_id: UUID4

    class Config:
        from_attributes = True
