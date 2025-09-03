
from pydantic import BaseModel, UUID4
import datetime
from typing import Optional
from ..models.movimentacoes_estoque import TipoMovimentacao

class MovimentacaoEstoqueBase(BaseModel):
    produto_id: UUID4
    tipo: TipoMovimentacao
    quantidade: float
    observacao: Optional[str] = None

class MovimentacaoEstoqueCreate(MovimentacaoEstoqueBase):
    paciente_id: Optional[UUID4] = None
    tratamento_id: Optional[UUID4] = None
    servico_id: Optional[UUID4] = None

class MovimentacaoEstoque(MovimentacaoEstoqueBase):
    id: UUID4
    tenant_id: UUID4
    paciente_id: Optional[UUID4] = None
    tratamento_id: Optional[UUID4] = None
    servico_id: Optional[UUID4] = None
    data: datetime.datetime

    class Config:
        from_attributes = True
