
import uuid
import enum
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db.base_class import Base

class MetodoPagamento(str, enum.Enum):
    pix = "Pix"
    cartao_credito = "Cartão de Crédito"
    cartao_debito = "Cartão de Débito"
    dinheiro = "Dinheiro"
    transferencia = "Transferência Bancária"

class Pagamento(Base):
    __tablename__ = "pagamentos"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PG_UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    paciente_id = Column(PG_UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False)
    plano_custo_id = Column(PG_UUID(as_uuid=True), ForeignKey("planos_custo.id"), nullable=True)
    orcamento_id = Column(PG_UUID(as_uuid=True), ForeignKey("orcamentos.id"), nullable=True)
    
    valor = Column(Numeric(12, 2), nullable=False)
    data_pagamento = Column(TIMESTAMP, nullable=False, server_default=func.now())
    metodo_pagamento = Column(ENUM(MetodoPagamento, name='metodo_pagamento_enum', create_type=False), nullable=False)
    observacoes = Column(Text, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    paciente = relationship("Paciente")
    plano_custo = relationship("PlanoCusto")
    orcamento = relationship("Orcamento", back_populates="pagamentos")
