
import uuid
from sqlalchemy import Column, String, Integer, TIMESTAMP, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db.base_class import Base

class Estoque(Base):
    __tablename__ = "estoque"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PG_UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    nome = Column(String(255), nullable=False)
    quantidade = Column(Numeric(10, 3), nullable=False, default=0)
    min_quantidade = Column(Numeric(10, 3), nullable=False, default=0)
    unidade = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    movimentacoes = relationship("MovimentacaoEstoque", back_populates="produto", cascade="all, delete-orphan")
    orcamento_itens = relationship("OrcamentoItem", back_populates="produto")
