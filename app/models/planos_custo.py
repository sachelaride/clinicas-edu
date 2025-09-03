
import uuid
import enum
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db.base_class import Base

class PlanoCustoStatus(enum.Enum):
    pendente = "pendente"
    aprovado = "aprovado"
    cancelado = "cancelado"

class PlanoCusto(Base):
    __tablename__ = "planos_custo"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PG_UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    paciente_id = Column(PG_UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False)
    tratamento_id = Column(PG_UUID(as_uuid=True), ForeignKey("tratamentos.id"), nullable=True)
    status = Column(ENUM(PlanoCustoStatus, name='plano_custo_status', create_type=False), default=PlanoCustoStatus.pendente, nullable=False)
    valor_total = Column(Numeric(12, 2), default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    itens = relationship("PlanoCustoItem", back_populates="plano_custo", cascade="all, delete-orphan")
