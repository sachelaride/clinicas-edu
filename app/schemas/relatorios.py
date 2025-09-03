
from pydantic import BaseModel, UUID4
from typing import List, Dict

class HorasAtendimentoAcademico(BaseModel):
    profissional_id: UUID4
    nome_profissional: str
    total_horas: float

class RelatorioHorasAtendimento(BaseModel):
    data_inicio: str
    data_fim: str
    relatorio: List[HorasAtendimentoAcademico]

class ProcedimentoPorTipo(BaseModel):
    servico_nome: str
    quantidade: int

class ProcedimentosPorEstudante(BaseModel):
    profissional_id: UUID4
    nome_profissional: str
    procedimentos: List[ProcedimentoPorTipo]

class RelatorioProcedimentosPorEstudante(BaseModel):
    data_inicio: str
    data_fim: str
    relatorio: List[ProcedimentosPorEstudante]

class TempoMedioAprovacaoOrientador(BaseModel):
    orientador_id: UUID4
    nome_orientador: str
    tempo_medio_aprovacao_horas: float

class RelatorioTempoMedioAprovacao(BaseModel):
    data_inicio: str
    data_fim: str
    relatorio: List[TempoMedioAprovacaoOrientador]

class AgendamentosPorStatus(BaseModel):
    status: str
    quantidade: int

class AgendamentosPorProfissional(BaseModel):
    profissional_id: UUID4
    nome_profissional: str
    quantidade: int

class AgendamentosPorServico(BaseModel):
    servico_id: UUID4
    nome_servico: str
    quantidade: int

class VisaoGeralAgendamentos(BaseModel):
    data_inicio: str
    data_fim: str
    total_agendamentos: int
    agendamentos_por_status: List[AgendamentosPorStatus]
    agendamentos_por_profissional: List[AgendamentosPorProfissional]
    agendamentos_por_servico: List[AgendamentosPorServico]

class TratamentosPorStatus(BaseModel):
    status: str
    quantidade: int

class RelatorioTratamentosPorStatus(BaseModel):
    data_inicio: str
    data_fim: str
    relatorio: List[TratamentosPorStatus]

class ResumoFinanceiro(BaseModel):
    data_inicio: str
    data_fim: str
    total_planos_custo: int
    total_valor_aprovado: float
    total_valor_pendente: float
    total_valor_cancelado: float

class CustoServicoTratamento(BaseModel):
    servico_nome: str
    custo: float

class CustoTratamento(BaseModel):
    tratamento_id: UUID4
    nome_tratamento: str
    nome_paciente: str
    custo_total_tratamento: float
    servicos_incluidos: List[CustoServicoTratamento]

class RelatorioCustosTratamento(BaseModel):
    data_inicio: str
    data_fim: str
    relatorio: List[CustoTratamento]
    total_geral_custos: float
