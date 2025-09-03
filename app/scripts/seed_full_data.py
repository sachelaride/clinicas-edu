#!/usr/bin/env python

import asyncio
import uuid
from datetime import date, datetime, timedelta
import random

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# Adjust the path to import from the parent directory
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.db.database import AsyncSessionLocal
from app.models.tenants import Tenant
from app.models.users import SystemUser
from app.models.roles import UserRole
from app.models.responsaveis import Responsavel
from app.models.pacientes import Paciente
from app.models.servicos import Servico
from app.models.agendamentos import Agendamento, AppointmentStatus
from app.models.prontuarios import Prontuario
from app.models.tratamentos import Tratamento, TreatmentStatus
from app.models.documentos_paciente import DocumentoPaciente
from app.core import security # For password hashing

async def seed_full_data():
    """Seeds the database with a complete set of data for testing."""
    print("Iniciando o script para cadastrar dados completos...")
    
    session: AsyncSession = AsyncSessionLocal()
    
    try:
        # Get the first tenant
        result = await session.execute(select(Tenant))
        tenant = result.scalars().first()
        if not tenant:
            print("Nenhum tenant encontrado. Execute o script seed_initial_data.py primeiro.")
            return
        print(f"Usando o tenant: {tenant.nome}")

        # Create Responsaveis
        print("Criando responsáveis...")
        responsaveis_to_create = [
            {"nome": "Maria Silva", "telefone": "(11)98765-4321", "email": "maria.silva@example.com", "documento": "123.456.789-00"},
            {"nome": "João Santos", "telefone": "(21)99887-6543", "email": "joao.santos@example.com", "documento": "098.765.432-11"},
        ]
        created_responsaveis = []
        for resp_data in responsaveis_to_create:
            new_resp = Responsavel(**resp_data)
            session.add(new_resp)
            created_responsaveis.append(new_resp)
        await session.flush()

        # Create Pacientes
        print("Criando pacientes...")
        pacientes_to_create = [
            {"nome": "Criança Feliz", "data_nascimento": date(2015, 5, 10), "genero": "Masculino", "responsavel_id": created_responsaveis[0].id, "tenant_id": tenant.id},
            {"nome": "Adolescente Saudável", "data_nascimento": date(2008, 8, 20), "genero": "Feminino", "responsavel_id": created_responsaveis[1].id, "tenant_id": tenant.id},
            {"nome": "Adulto Ocupado", "data_nascimento": date(1990, 1, 1), "genero": "Masculino", "tenant_id": tenant.id},
        ]
        created_pacientes = []
        for i, pac_data in enumerate(pacientes_to_create):
            # Generate a simple client_code for demonstration
            pac_data["client_code"] = f"CLI-{i+1:04d}" # Example: CLI-0001, CLI-0002
            new_pac = Paciente(**pac_data)
            session.add(new_pac)
            created_pacientes.append(new_pac)
        await session.flush()

        # Create Servicos
        print("Criando serviços...")
        servicos_to_create = [
            {"nome": "Consulta de Rotina", "descricao": "Consulta de acompanhamento", "valor": 150.00, "tenant_id": tenant.id},
            {"nome": "Limpeza Dental", "descricao": "Profilaxia e limpeza", "valor": 200.00, "tenant_id": tenant.id},
            {"nome": "Restauração", "descricao": "Restauração de dente", "valor": 350.00, "tenant_id": tenant.id},
        ]
        created_servicos = []
        for serv_data in servicos_to_create:
            new_serv = Servico(**serv_data)
            session.add(new_serv)
            created_servicos.append(new_serv)
        await session.flush()

        # Get a user to be the academico
        result = await session.execute(select(SystemUser))
        academico = result.scalars().first()
        if not academico:
            print("Nenhum usuário encontrado. Execute o script seed_initial_data.py primeiro.")
            return

        # Create Agendamentos
        print("Criando agendamentos...")
        agendamentos_to_create = [
            {"paciente_id": created_pacientes[0].id, "servico_id": created_servicos[0].id, "inicio": datetime.now() + timedelta(days=7), "fim": datetime.now() + timedelta(days=7, hours=1), "status": AppointmentStatus.agendado, "tenant_id": tenant.id, "academico_id": academico.id},
            {"paciente_id": created_pacientes[1].id, "servico_id": created_servicos[1].id, "inicio": datetime.now() + timedelta(days=10), "fim": datetime.now() + timedelta(days=10, hours=1), "status": AppointmentStatus.agendado, "tenant_id": tenant.id, "academico_id": academico.id},
        ]
        for agend_data in agendamentos_to_create:
            new_agend = Agendamento(**agend_data)
            session.add(new_agend)
        await session.flush()

        # Create Prontuarios
        print("Criando prontuários...")
        prontuarios_to_create = [
            {"paciente_id": created_pacientes[0].id, "conteudo": "Paciente apresenta bom desenvolvimento."},
            {"paciente_id": created_pacientes[1].id, "conteudo": "Paciente com histórico de cáries."},
        ]
        for pront_data in prontuarios_to_create:
            new_pront = Prontuario(**pront_data)
            session.add(new_pront)
        await session.flush()

        # Create Tratamentos
        print("Criando tratamentos...")
        tratamentos_to_create = [
            {"paciente_id": created_pacientes[1].id, "nome": "Tratamento de Canal", "descricao": "Tratamento de canal", "status": TreatmentStatus.em_progresso, "tenant_id": tenant.id},
        ]
        for trat_data in tratamentos_to_create:
            new_trat = Tratamento(**trat_data)
            session.add(new_trat)
        await session.flush()

        # Create Documentos
        print("Criando documentos...")
        documentos_to_create = [
            {"paciente_id": created_pacientes[0].id, "nome_arquivo": "exame.pdf", "caminho_arquivo": "/data/uploads/exame.pdf", "tipo_documento": "Exame de Sangue"},
        ]
        for doc_data in documentos_to_create:
            new_doc = DocumentoPaciente(**doc_data)
            session.add(new_doc)
        await session.flush()

        await session.commit()
        print("\nDados completos cadastrados com sucesso!")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        await session.rollback()
    finally:
        await session.close()
        print("Script finalizado.")

if __name__ == "__main__":
    asyncio.run(seed_full_data())