import uuid
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db.base_class import Base

class DocumentoPaciente(Base):
    __tablename__ = "documentos_paciente"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paciente_id = Column(PG_UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False)
    nome_arquivo = Column(String(255), nullable=False) # Original file name
    caminho_arquivo = Column(String(512), nullable=False) # Stored path on disk
    tipo_documento = Column(String(100), nullable=True) # e.g., "Consentimento", "Exame", "Receita"
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    paciente = relationship("Paciente", backref="documentos")
