import uuid
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db.base_class import Base

class Prontuario(Base):
    __tablename__ = "prontuarios"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paciente_id = Column(PG_UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False)
    agendamento_id = Column(PG_UUID(as_uuid=True), ForeignKey("agendamentos.id"), nullable=True) # Link to appointment
    servico_id = Column(PG_UUID(as_uuid=True), ForeignKey("servicos.id"), nullable=True) # Link to service/procedure
    conteudo = Column(Text, nullable=False) # The actual record content (text)
    caminho_arquivo = Column(String(512), nullable=True) # Path to the associated file
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    paciente = relationship("Paciente", backref="prontuarios")
    agendamento = relationship("Agendamento", backref="prontuario")
    servico = relationship("Servico", backref="prontuario")
