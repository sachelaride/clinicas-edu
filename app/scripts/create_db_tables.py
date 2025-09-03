#!/usr/bin/env python

import asyncio
import sys
import os

from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM, CreateEnumType


# Adjust the path to import from the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.db.base_class import Base
from app.db.database import engine

# Import all models to ensure they are registered with Base.metadata
# This is crucial for create_all() to find all tables.
import app.models.agendamentos
import app.models.consentimentos_paciente
import app.models.despesas
import app.models.documentos_paciente
import app.models.estoque
import app.models.feriados
import app.models.menu_permissions
import app.models.movimentacoes_estoque
import app.models.pacientes
import app.models.pagamentos
import app.models.planos_custo_itens
import app.models.planos_custo
import app.models.prontuarios
import app.models.responsaveis
import app.models.roles
import app.models.servicos
import app.models.tenant_configs
import app.models.tenants
import app.models.tratamento_servicos
import app.models.tratamentos

import app.models.users

# Import ENUM classes
from app.models.roles import UserRole
from app.models.tratamentos import TreatmentStatus
from app.models.tenant_configs import ConfigType, ConfigKey

from app.models.planos_custo import PlanoCustoStatus
from app.models.pagamentos import MetodoPagamento
from app.models.movimentacoes_estoque import TipoMovimentacao
from app.models.menu_permissions import MenuKey
from app.models.agendamentos import AppointmentStatus

async def create_db_tables():
    """Creates all database tables defined in the models."""
    print("Criando tabelas do banco de dados...")
    async with engine.begin() as conn:
        # Create ENUM types explicitly
        await conn.run_sync(lambda sync_conn: PG_ENUM(UserRole, name='user_role', create_type=True).create(sync_conn))
        await conn.run_sync(lambda sync_conn: PG_ENUM(TreatmentStatus, name='treatment_status', create_type=True).create(sync_conn))
        await conn.run_sync(lambda sync_conn: PG_ENUM(ConfigType, name='config_type', create_type=True).create(sync_conn))
        await conn.run_sync(lambda sync_conn: PG_ENUM(ConfigKey, name='config_key', create_type=True).create(sync_conn))
        
        await conn.run_sync(lambda sync_conn: PG_ENUM(PlanoCustoStatus, name='plano_custo_status', create_type=True).create(sync_conn))
        await conn.run_sync(lambda sync_conn: PG_ENUM(MetodoPagamento, name='metodo_pagamento_enum', create_type=True).create(sync_conn))
        await conn.run_sync(lambda sync_conn: PG_ENUM(TipoMovimentacao, name='tipo_movimentacao_enum', create_type=True).create(sync_conn))
        await conn.run_sync(lambda sync_conn: PG_ENUM(MenuKey, name='menu_key', create_type=True).create(sync_conn))
        await conn.run_sync(lambda sync_conn: PG_ENUM(AppointmentStatus, name='appointment_status', create_type=True).create(sync_conn))

        # Then create tables
        await conn.run_sync(Base.metadata.create_all)
    print("Tabelas criadas com sucesso!")

if __name__ == "__main__":
    asyncio.run(create_db_tables())