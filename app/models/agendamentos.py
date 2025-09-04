import uuid
import enum
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ENUM
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db.base_class import Base
from ..models.pacientes import Paciente
from ..models.servicos import Servico
from ..models.users import SystemUser
from ..models.tratamentos import Tratamento

class AppointmentStatus(str, enum.Enum):
    agendado = "agendado"
    iniciado = "iniciado"
    aguardando = "aguardando"
    em_atendimento = "em_atendimento"
    concluido = "concluido"
    cancelado = "cancelado"

class Agendamento(Base):
    __tablename__ = "agendamentos"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PG_UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    paciente_id = Column(PG_UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False)
    academico_id = Column(PG_UUID(as_uuid=True), ForeignKey("system_users.id"), nullable=False)
    orientador_id = Column(PG_UUID(as_uuid=True), ForeignKey("system_users.id"), nullable=True)
    tratamento_id = Column(PG_UUID(as_uuid=True), ForeignKey("tratamentos.id"), nullable=True)
    servico_id = Column(PG_UUID(as_uuid=True), ForeignKey("servicos.id"), nullable=True)
    tipo_atendimento = Column(String(255), nullable=True)
    inicio = Column(TIMESTAMP, nullable=False)
    fim = Column(TIMESTAMP, nullable=False)
    status = Column(ENUM(AppointmentStatus, name='appointment_status', create_type=False), default=AppointmentStatus.agendado, nullable=False)
    observacoes = Column(String(500), nullable=True)
    hora_inicio_atendimento = Column(TIMESTAMP, nullable=True)
    hora_fim_atendimento = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    paciente = relationship("Paciente", back_populates="agendamentos")
    academico = relationship("SystemUser", foreign_keys=[academico_id])
    orientador = relationship("SystemUser", foreign_keys=[orientador_id])
    tratamento = relationship("Tratamento", back_populates="agendamentos")
    servico = relationship("Servico", back_populates="agendamentos")

class AgendamentoDetalhesView(Base):
    __tablename__ = "v_agendamentos_detalhes"
    __table_args__ = {'extend_existing': True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    tenant_id = Column(PG_UUID(as_uuid=True))
    inicio = Column(TIMESTAMP)
    fim = Column(TIMESTAMP)
    status = Column(ENUM(AppointmentStatus, name='appointment_status', create_type=False))
    tipo_atendimento = Column(String(255))
    paciente_nome = Column(String(255))
    academico_nome = Column(String(255))
    orientador_nome = Column(String(255))
    servico_nome = Column(String(255))
    tratamento_nome = Column(String(255))
