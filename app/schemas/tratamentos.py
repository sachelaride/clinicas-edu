from pydantic import BaseModel, UUID4
import datetime
from typing import Optional, List
from ..models.tratamentos import TreatmentStatus
from .tratamento_servicos import TratamentoServico

class ServicoTratamentoCreate(BaseModel):
    servico_id: UUID4
    academico_id: Optional[UUID4] = None
    monitor_id: Optional[UUID4] = None

class TratamentoBase(BaseModel):
    paciente_id: Optional[UUID4]
    nome: str
    descricao: Optional[str] = None
    status: TreatmentStatus = TreatmentStatus.planejado

class TratamentoCreate(TratamentoBase):
    servicos: Optional[List[ServicoTratamentoCreate]] = None

class TratamentoUpdate(TratamentoBase):
    paciente_id: Optional[UUID4] = None
    nome: Optional[str] = None
    descricao: Optional[str] = None
    status: Optional[TreatmentStatus] = None
    servicos: Optional[List[ServicoTratamentoCreate]] = None

class Tratamento(TratamentoBase):
    id: UUID4
    tenant_id: UUID4
    created_at: datetime.datetime
    updated_at: datetime.datetime
    servicos: List[TratamentoServico] = []

    class Config:
        from_attributes = True
