import uuid
from sqlalchemy import Column, String, Date, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
from ..db.base_class import Base

class Feriado(Base):
    __tablename__ = "feriados"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PG_UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    data = Column(Date, nullable=False) # Data do feriado
    nome = Column(String(255), nullable=False) # Nome do feriado
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    __table_args__ = (UniqueConstraint('tenant_id', 'data', name='_tenant_data_uc'),)
