
import uuid
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
from ..db.base_class import Base

class ConsentimentoPaciente(Base):
    __tablename__ = "consentimentos_paciente"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PG_UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    paciente_id = Column(PG_UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False)
    tipo_consentimento = Column(String(255), nullable=False)
    data_consentimento = Column(TIMESTAMP, server_default=func.now())
    arquivo_url = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
