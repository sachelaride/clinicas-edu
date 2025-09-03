# app/models/__init__.py

from .agendamentos import Agendamento, AppointmentStatus, AgendamentoDetalhesView
from .pacientes import Paciente
from .servicos import Servico
from .users import SystemUser
from .tratamentos import Tratamento, TreatmentStatus
from .tratamento_servicos import TratamentoServico
from .roles import UserRole
from .tenants import Tenant
from .responsaveis import Responsavel
from .estoque import Estoque
from .movimentacoes_estoque import MovimentacaoEstoque
from .prontuarios import Prontuario
from .planos_custo import PlanoCusto
from .planos_custo_itens import PlanoCustoItem
from .pagamentos import Pagamento
from .despesas import Despesa
from .documentos_paciente import DocumentoPaciente
from .consentimentos_paciente import ConsentimentoPaciente
from .feriados import Feriado
from .menu_permissions import MenuPermission
from .tenant_configs import TenantConfig
from .orcamentos import Orcamento, OrcamentoItem, OrcamentoStatus