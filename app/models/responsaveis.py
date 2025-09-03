import uuid
from sqlalchemy import Column, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db.base_class import Base

class Responsavel(Base):
    __tablename__ = "responsaveis"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(255), nullable=False)
    telefone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    documento = Column(String(255), nullable=True) # e.g., CPF, RG
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    pacientes = relationship("Paciente", back_populates="responsavel")
    orcamentos = relationship("Orcamento", back_populates="responsavel")