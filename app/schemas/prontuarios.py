# Importações do Pydantic para criação de schemas e de tipos padrão do Python.
from pydantic import BaseModel, UUID4
import datetime
from typing import Optional, Dict, Any, List
import enum
from ..schemas.pacientes import Paciente
from ..schemas.tratamentos import Tratamento
from ..schemas.servicos import Servico
from ..schemas.users import User

# Define um Enum para os status de revisão. Herdar de `str` e `enum.Enum` permite que o Pydantic
# trate os valores tanto como strings (ex: em JSON) quanto como membros de um Enum no código Python.
class ReviewStatus(str, enum.Enum):
    pendente = "pendente"
    aprovado = "aprovado"
    reprovado = "reprovado"

# Schema Base: Contém os campos comuns a todas as outras variações de schemas de Prontuário.
# Isso evita repetição de código e estabelece um contrato de dados base.
class ProntuarioBase(BaseModel):
    paciente_id: UUID4
    agendamento_id: Optional[UUID4] = None
    dados_json: Dict[str, Any]
    pdf_url: Optional[str] = None
    orientador_id: Optional[UUID4] = None
    status_revisao: ReviewStatus = ReviewStatus.pendente
    feedback_orientador: Optional[str] = None

# Schema para Criação: Usado para validar os dados recebidos ao criar um novo prontuário.
# Herda todos os campos de ProntuarioBase. A declaração `pass` indica que não há campos adicionais
# ou modificações necessárias para a operação de criação.
class ProntuarioCreate(ProntuarioBase):
    pass

# Schema para Atualização: Usado para validar os dados ao atualizar um prontuário existente.
# Herda de ProntuarioBase, mas torna todos os campos opcionais. Isso permite que o cliente
# envie apenas os campos que deseja modificar (atualização parcial ou PATCH).
class ProntuarioUpdate(ProntuarioBase):
    paciente_id: Optional[UUID4] = None
    dados_json: Optional[Dict[str, Any]] = None
    pdf_url: Optional[str] = None
    status_revisao: Optional[ReviewStatus] = None
    feedback_orientador: Optional[str] = None

# Schema para Leitura (Resposta): Usado para formatar os dados que são enviados de volta ao cliente.
# Herda os campos de ProntuarioBase e adiciona os campos que são gerados pelo banco de dados (id, tenant_id, timestamps).
class Prontuario(ProntuarioBase):
    id: UUID4
    tenant_id: UUID4
    created_at: datetime.datetime
    updated_at: datetime.datetime

    # A classe interna `Config` do Pydantic permite configurar o comportamento do schema.
    class Config:
        # `from_attributes = True` (anteriormente `orm_mode`) permite que o Pydantic crie uma instância do schema
        # diretamente a partir de um objeto de modelo do SQLAlchemy (ex: `Prontuario(db_prontuario)`).
        # Ele lerá os atributos do objeto em vez de esperar um dicionário.
        from_attributes = True

# Schema específico para a rota de revisão de prontuário.
# Define um subconjunto de campos permitidos para a operação de revisão, tornando a API mais segura e explícita.
class ProntuarioReview(BaseModel):
    status_revisao: ReviewStatus
    feedback_orientador: Optional[str] = None

class ProntuarioPDFData(BaseModel):
    prontuario: Prontuario
    paciente: Paciente
    tratamento: Optional[Tratamento] = None
    servicos: List[Servico] = []
    monitor: Optional[User] = None
    academico: Optional[User] = None
    gestor: Optional[User] = None
