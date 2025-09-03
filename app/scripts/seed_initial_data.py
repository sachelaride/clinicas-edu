#!/usr/bin/env python

import asyncio
import uuid

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
from app.core import security # For password hashing

async def seed_initial_data():
    """Seeds the database with initial tenants and admin_global users."""
    print("Iniciando o script para cadastrar dados iniciais...")
    
    session: AsyncSession = AsyncSessionLocal()
    
    try:
        # 1. Create Tenants
        tenants_to_create = [
            {"nome": "Clinica Alpha", "cnpj": "11.111.111/0001-11"},
            {"nome": "Clinica Beta", "cnpj": "22.222.222/0001-22"},
            {"nome": "Clinica Gamma", "cnpj": "33.333.333/0001-33"},
            {"nome": "Clinica Delta", "cnpj": "44.444.444/0001-44"},
        ]
        
        created_tenants = []
        for tenant_data in tenants_to_create:
            existing_tenant = await session.execute(select(Tenant).where(Tenant.cnpj == tenant_data['cnpj']))
            if existing_tenant.scalars().first() is None:
                new_tenant = Tenant(id=uuid.uuid4(), nome=tenant_data['nome'], cnpj=tenant_data['cnpj'])
                session.add(new_tenant)
                created_tenants.append(new_tenant)
                print(f"  + Criando Tenant: {new_tenant.nome}")
            else:
                print(f"  - Tenant {tenant_data['nome']} já existe. Pulando.")
                created_tenants.append(existing_tenant.scalars().first()) # Get existing tenant
        
        await session.flush() # Flush to get IDs for newly created tenants

        # 2. Create Admin Global Users
        users_to_create = [
            {"username": "admin01", "nome": "Admin User 01", "email": "admin01@example.com", "password": "password"},
            {"username": "admin02", "nome": "Admin User 02", "email": "admin02@example.com", "password": "password"},
            {"username": "admin03", "nome": "Admin User 03", "email": "admin03@example.com", "password": "password"},
            {"username": "admin04", "nome": "Admin User 04", "email": "admin04@example.com", "password": "password"},
        ]

        for i, user_data in enumerate(users_to_create):
            existing_user = await session.execute(select(SystemUser).where(SystemUser.username == user_data['username']))
            if existing_user.scalars().first() is None:
                # Link user to a created tenant (round-robin or sequential)
                if created_tenants:
                    tenant_for_user = created_tenants[i % len(created_tenants)]
                else:
                    print(f"Aviso: Nenhum tenant disponível para vincular o usuário {user_data['username']}.")
                    tenant_for_user = None

                hashed_password = security.get_password_hash(user_data['password'])
                new_user = SystemUser(
                    id=uuid.uuid4(),
                    nome=user_data['nome'],
                    email=user_data['email'],
                    username=user_data['username'],
                    senha_hash=hashed_password,
                    role=UserRole.admin_global,
                    default_tenant_id=tenant_for_user.id if tenant_for_user else None # Link to tenant
                )
                session.add(new_user)
                print(f"  + Criando Usuário Admin: {new_user.username} vinculado a {tenant_for_user.nome if tenant_for_user else 'Nenhum'}")
            else:
                print(f"  - Usuário Admin {user_data['username']} já existe. Pulando.")
        
        await session.commit()
        print("\nDados iniciais cadastrados com sucesso!")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        await session.rollback()
    finally:
        await session.close()
        print("Script finalizado.")

if __name__ == "__main__":
    asyncio.run(seed_initial_data())
