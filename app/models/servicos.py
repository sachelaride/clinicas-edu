import uuid
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
from ..db.base_class import Base

class Servico(Base):
    __tablename__ = "servicos"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(255), nullable=False)
    valor = Column(Numeric(12, 2), nullable=False)
    descricao = Column(String, nullable=True) # Added descricao column
    tenant_id = Column(PG_UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    movimentacoes = relationship("MovimentacaoEstoque", back_populates="servico")
    agendamentos = relationship("Agendamento", back_populates="servico")
    orcamento_itens = relationship("OrcamentoItem", back_populates="servico")
