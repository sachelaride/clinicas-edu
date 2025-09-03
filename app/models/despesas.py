
import uuid
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
from ..db.base_class import Base

class Despesa(Base):
    __tablename__ = "despesas"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PG_UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    
    descricao = Column(String(255), nullable=False)
    valor = Column(Numeric(12, 2), nullable=False)
    categoria = Column(String(100), nullable=True)
    data_despesa = Column(TIMESTAMP, nullable=False, server_default=func.now())

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
