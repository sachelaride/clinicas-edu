
from pydantic import BaseModel, UUID4
from typing import Optional

class TratamentoServicoBase(BaseModel):
    servico_id: UUID4
    quantidade: int = 1
    academico_id: Optional[UUID4] = None
    monitor_id: Optional[UUID4] = None

class TratamentoServicoCreate(TratamentoServicoBase):
    pass

class TratamentoServico(TratamentoServicoBase):
    id: UUID4
    tratamento_id: UUID4
    tenant_id: UUID4

    class Config:
        from_attributes = True
