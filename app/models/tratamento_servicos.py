
from sqlalchemy import Column, ForeignKey, Integer, UUID
from sqlalchemy.orm import relationship
from ..db.base_class import Base
import uuid

class TratamentoServico(Base):
    __tablename__ = "tratamento_servicos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    tratamento_id = Column(UUID(as_uuid=True), ForeignKey("tratamentos.id"), nullable=False)
    servico_id = Column(UUID(as_uuid=True), ForeignKey("servicos.id"), nullable=False)
    academico_id = Column(UUID(as_uuid=True), ForeignKey("system_users.id"), nullable=True)
    monitor_id = Column(UUID(as_uuid=True), ForeignKey("system_users.id"), nullable=True)
    quantidade = Column(Integer, default=1)

    tratamento = relationship("Tratamento", back_populates="servicos")
    servico = relationship("Servico")
    academico = relationship("SystemUser", foreign_keys=[academico_id])
    monitor = relationship("SystemUser", foreign_keys=[monitor_id])
