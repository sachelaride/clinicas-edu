import uuid
import enum
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ENUM
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db.base_class import Base

class TreatmentStatus(enum.Enum):
    planejado = "planejado"
    em_progresso = "em_progresso"
    ativo = "ativo"
    concluido = "concluido"
    cancelado = "cancelado"

class Tratamento(Base):
    __tablename__ = "tratamentos"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PG_UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    paciente_id = Column(PG_UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=True)
    orcamento_id = Column(PG_UUID(as_uuid=True), ForeignKey("orcamentos.id"), nullable=True)
    nome = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=True)
    status = Column(ENUM(TreatmentStatus, name='treatment_status', create_type=False), default=TreatmentStatus.planejado, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    servicos = relationship("TratamentoServico", back_populates="tratamento", cascade="all, delete-orphan")
    agendamentos = relationship("Agendamento", back_populates="tratamento")
    movimentacoes = relationship("MovimentacaoEstoque", back_populates="tratamento")
    orcamento = relationship("Orcamento", back_populates="tratamentos", foreign_keys=[orcamento_id])
