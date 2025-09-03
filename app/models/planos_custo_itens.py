
import uuid
from sqlalchemy import Column, ForeignKey, Integer, Numeric, UUID
from sqlalchemy.orm import relationship
from ..db.base_class import Base

class PlanoCustoItem(Base):
    __tablename__ = "planos_custo_itens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    plano_custo_id = Column(UUID(as_uuid=True), ForeignKey("planos_custo.id"), nullable=False)
    servico_id = Column(UUID(as_uuid=True), ForeignKey("servicos.id"), nullable=False)
    quantidade = Column(Integer, default=1)
    valor = Column(Numeric(12, 2), nullable=False)

    plano_custo = relationship("PlanoCusto", back_populates="itens")
    servico = relationship("Servico")
