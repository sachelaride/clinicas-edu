
import uuid
import enum
from sqlalchemy import Column, String, Integer, TIMESTAMP, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db.base_class import Base

class TipoMovimentacao(enum.Enum):
    entrada = "entrada"
    saida = "saida"

class MovimentacaoEstoque(Base):
    __tablename__ = "movimentacoes_estoque"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PG_UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    produto_id = Column(PG_UUID(as_uuid=True), ForeignKey("estoque.id"), nullable=False)
    paciente_id = Column(PG_UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=True)
    tratamento_id = Column(PG_UUID(as_uuid=True), ForeignKey("tratamentos.id"), nullable=True)
    servico_id = Column(PG_UUID(as_uuid=True), ForeignKey("servicos.id"), nullable=True)
    tipo = Column(ENUM(TipoMovimentacao, name='tipo_movimentacao_enum', create_type=False), nullable=False)
    quantidade = Column(Numeric(10, 3), nullable=False)
    observacao = Column(Text, nullable=True)
    data = Column(TIMESTAMP, server_default=func.now())
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    produto = relationship("Estoque", back_populates="movimentacoes")
    paciente = relationship("Paciente")
    tratamento = relationship("Tratamento")
    servico = relationship("Servico")
