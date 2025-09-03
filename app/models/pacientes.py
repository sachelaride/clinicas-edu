import uuid
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Date
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db.base_class import Base

class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PG_UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    responsavel_id = Column(PG_UUID(as_uuid=True), ForeignKey("responsaveis.id"), nullable=True)
    client_code = Column(String(50), unique=True, nullable=False) # New client code field
    nome = Column(String(255), nullable=False)
    data_nascimento = Column(Date, nullable=False)
    genero = Column(String(50), nullable=False)
    endereco = Column(String(255), nullable=True)
    telefone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    responsavel = relationship("Responsavel", back_populates="pacientes")
    agendamentos = relationship("Agendamento", back_populates="paciente")
    movimentacoes = relationship("MovimentacaoEstoque", back_populates="paciente")
    orcamentos = relationship("Orcamento", back_populates="paciente")