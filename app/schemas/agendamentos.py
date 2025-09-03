from pydantic import BaseModel, UUID4, validator
import datetime
from typing import Optional
from ..models.agendamentos import AppointmentStatus
from .pacientes import Paciente
from .servicos import Servico
from .users import User, UserSimple
from .tratamentos import Tratamento

class AgendamentoBase(BaseModel):
    paciente_id: Optional[UUID4] = None
    academico_id: Optional[UUID4] = None
    orientador_id: Optional[UUID4] = None
    tratamento_id: Optional[UUID4] = None
    servico_id: Optional[UUID4] = None
    tipo_atendimento: Optional[str] = None
    inicio: Optional[datetime.datetime] = None
    fim: Optional[datetime.datetime] = None
    status: Optional[AppointmentStatus] = AppointmentStatus.agendado
    observacoes: Optional[str] = None
    hora_inicio_atendimento: Optional[datetime.datetime] = None
    hora_fim_atendimento: Optional[datetime.datetime] = None

    @validator('fim')
    def validate_time_range(cls, fim, values):
        if 'inicio' in values and fim <= values['inicio']:
            raise ValueError('End time must be after start time')
        return fim

class AgendamentoCreate(AgendamentoBase):
    paciente_id: UUID4
    academico_id: UUID4
    orientador_id: Optional[UUID4] = None
    tratamento_id: Optional[UUID4] = None
    servico_id: Optional[UUID4] = None
    tipo_atendimento: Optional[str] = None
    inicio: datetime.datetime
    fim: datetime.datetime
    status: AppointmentStatus = AppointmentStatus.agendado
    observacoes: Optional[str] = None

class AgendamentoUpdate(AgendamentoBase):
    pass

class Agendamento(AgendamentoBase):
    id: UUID4
    tenant_id: UUID4
    created_at: datetime.datetime
    updated_at: datetime.datetime
    
    paciente: Paciente
    academico: UserSimple
    orientador: Optional[UserSimple] = None
    tratamento: Optional[Tratamento] = None
    servico: Optional[Servico] = None

    class Config:
        from_attributes = True

class AgendamentoDetalhes(BaseModel):
    id: UUID4
    tenant_id: UUID4
    inicio: datetime.datetime
    fim: datetime.datetime
    status: AppointmentStatus
    tipo_atendimento: Optional[str] = None
    paciente_nome: str
    academico_nome: str
    orientador_nome: Optional[str] = None
    servico_nome: Optional[str] = None
    tratamento_nome: Optional[str] = None
    observacoes: Optional[str] = None
    hora_inicio_atendimento: Optional[datetime.datetime] = None
    hora_fim_atendimento: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True