#!/usr/bin/env python

import asyncio
import uuid
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# Adjust the path to import from the parent directory
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.db.database import AsyncSessionLocal  # Corrected import
from app.models.tenants import Tenant         # Corrected import
from app.models.feriados import Feriado        # Corrected import

# List of fixed national holidays (day, month)
HOLIDAYS = [
    (1, 1, "Confraternização Universal"),
    (21, 4, "Tiradentes"),
    (1, 5, "Dia do Trabalhador"),
    (7, 9, "Independência do Brasil"),
    (12, 10, "Nossa Senhora Aparecida"),
    (2, 11, "Finados"),
    (15, 11, "Proclamação da República"),
    (20, 11, "Dia Nacional de Zumbi e da Consciência Negra"),
    (25, 12, "Natal"),
]

YEAR = 2025

async def seed_holidays():
    """Seeds the database with national holidays for all tenants for a specific year."""
    print("Iniciando o script para cadastrar feriados...")
    
    session: AsyncSession = AsyncSessionLocal()  # Create a session directly from the factory
    
    try:
        # 1. Fetch all tenants
        print("Buscando todas as clínicas (tenants)...")
        tenants_result = await session.execute(select(Tenant))
        all_tenants = tenants_result.scalars().all()
        print(f"Encontrado {len(all_tenants)} tenants.")

        if not all_tenants:
            print("Nenhum tenant encontrado. Abortando.")
            return

        # 2. Iterate over tenants and holidays
        holidays_added_count = 0
        for tenant in all_tenants:
            print(f"\nProcessando tenant: {tenant.nome} (ID: {tenant.id})")
            for day, month, name in HOLIDAYS:
                holiday_date = date(YEAR, month, day)
                
                # 3. Check if holiday already exists for this tenant
                existing_holiday_result = await session.execute(
                    select(Feriado).where(
                        Feriado.tenant_id == tenant.id,
                        Feriado.data == holiday_date
                    )
                )
                existing_holiday = existing_holiday_result.scalars().first()

                if existing_holiday:
                    print(f"  - Feriado '{name}' em {holiday_date} já existe. Pulando.")
                else:
                    # 4. Create and add the new holiday
                    new_holiday = Feriado(
                        id=uuid.uuid4(),
                        tenant_id=tenant.id,
                        data=holiday_date,
                        nome=name
                    )
                    session.add(new_holiday)
                    holidays_added_count += 1
                    print(f"  + Adicionando feriado '{name}' em {holiday_date}.")
        
        # 5. Commit the session
        if holidays_added_count > 0:
            await session.commit()
            print(f"\n{holidays_added_count} novos feriados foram adicionados com sucesso!")
        else:
            print("\nNenhum feriado novo para adicionar.")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        await session.rollback()
    finally:
        await session.close()
        print("Script finalizado.")

if __name__ == "__main__":
    # This script needs the environment to be set up correctly
    # to find the database connection settings.
    # Ensure you run it with the correct environment activated.
    asyncio.run(seed_holidays())