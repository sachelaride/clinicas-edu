import uuid
import enum
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Text, Numeric, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ENUM
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db.base_class import Base

class OrcamentoStatus(enum.Enum):
    rascunho = "rascunho"
    enviado = "enviado"
    aprovado = "aprovado"
    rejeitado = "rejeitado"
    convertido = "convertido"
    cancelado = "cancelado"

class Orcamento(Base):
    __tablename__ = "orcamentos"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PG_UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    paciente_id = Column(PG_UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False)
    responsavel_id = Column(PG_UUID(as_uuid=True), ForeignKey("responsaveis.id"), nullable=True)
    academico_id = Column(PG_UUID(as_uuid=True), ForeignKey("system_users.id"), nullable=False)
    orientador_id = Column(PG_UUID(as_uuid=True), ForeignKey("system_users.id"), nullable=True)
    
    numero_orcamento = Column(String(50), unique=True, nullable=False)
    data_orcamento = Column(TIMESTAMP, nullable=False, server_default=func.now())
    data_validade = Column(TIMESTAMP, nullable=True)
    status = Column(ENUM(OrcamentoStatus, name='orcamento_status', create_type=False), 
                    default=OrcamentoStatus.rascunho, nullable=False)
    
    valor_total = Column(Numeric(10, 2), nullable=False, default=0)
    desconto_percentual = Column(Numeric(5, 2), nullable=False, default=0)
    desconto_valor = Column(Numeric(10, 2), nullable=False, default=0)
    valor_final = Column(Numeric(10, 2), nullable=False, default=0)
    
    observacoes = Column(Text, nullable=True)
    condicoes_pagamento = Column(Text, nullable=True)
    forma_pagamento = Column(String(100), nullable=True)
    
    aprovado_em = Column(TIMESTAMP, nullable=True)
    aprovado_por = Column(PG_UUID(as_uuid=True), ForeignKey("system_users.id"), nullable=True)
    rejeitado_em = Column(TIMESTAMP, nullable=True)
    rejeitado_por = Column(PG_UUID(as_uuid=True), ForeignKey("system_users.id"), nullable=True)
    motivo_rejeicao = Column(Text, nullable=True)
    
    convertido_em = Column(TIMESTAMP, nullable=True)
    convertido_por = Column(PG_UUID(as_uuid=True), ForeignKey("system_users.id"), nullable=True)
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    paciente = relationship("Paciente", back_populates="orcamentos")
    responsavel = relationship("Responsavel", back_populates="orcamentos")
    academico = relationship("SystemUser", foreign_keys=[academico_id])
    orientador = relationship("SystemUser", foreign_keys=[orientador_id])
    aprovador = relationship("SystemUser", foreign_keys=[aprovado_por])
    rejeitador = relationship("SystemUser", foreign_keys=[rejeitado_por])
    conversor = relationship("SystemUser", foreign_keys=[convertido_por])
    
    itens = relationship("OrcamentoItem", back_populates="orcamento", cascade="all, delete-orphan")
    pagamentos = relationship("Pagamento", back_populates="orcamento")
    tratamentos = relationship("Tratamento", back_populates="orcamento")

class OrcamentoItem(Base):
    __tablename__ = "orcamento_itens"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    orcamento_id = Column(PG_UUID(as_uuid=True), ForeignKey("orcamentos.id"), nullable=False)
    servico_id = Column(PG_UUID(as_uuid=True), ForeignKey("servicos.id"), nullable=True)
    produto_id = Column(PG_UUID(as_uuid=True), ForeignKey("estoque.id"), nullable=True)
    
    descricao = Column(String(255), nullable=False)
    quantidade = Column(Numeric(10, 3), nullable=False, default=1)
    valor_unitario = Column(Numeric(10, 2), nullable=False, default=0)
    valor_total = Column(Numeric(10, 2), nullable=False, default=0)
    
    observacoes = Column(Text, nullable=True)
    ordem = Column(String(10), nullable=False, default="1")
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    orcamento = relationship("Orcamento", back_populates="itens")
    servico = relationship("Servico", back_populates="orcamento_itens")
    produto = relationship("Estoque", back_populates="orcamento_itens")
