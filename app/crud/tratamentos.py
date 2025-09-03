import os
import re
import uuid
import datetime
from typing import Optional, List

from fastapi import HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import tratamentos
from app.models.tratamento_servicos import TratamentoServico
from ..schemas import tratamentos as schemas
from ..crud import tratamento_servicos as tratamento_servicos_crud
from ..crud import consentimentos_paciente as consent_crud

# Dependências usadas em finalizar_tratamento
from ..models import tenants as tenant_models, pacientes as paciente_models, users as user_models
from ..crud import agendamentos as agendamentos_crud
import jinja2
from xhtml2pdf import pisa


# Utilitário compatível com Pydantic v1/v2
def _model_to_dict(model, **kwargs):
    if hasattr(model, "model_dump"):
        return model.model_dump(**kwargs)  # Pydantic v2
    return model.dict(**kwargs)  # Pydantic v1


def _sanitize_dirname(name: Optional[str]) -> str:
    safe = name or "tenant"
    return re.sub(r"[^A-Za-z0-9._-]+", "_", safe).strip("._-") or "tenant"


async def get_tratamento(
    db: AsyncSession,
    tratamento_id: uuid.UUID,
    tenant_id: uuid.UUID,
):
    query = (
        select(tratamentos.Tratamento)
        .options(
            selectinload(tratamentos.Tratamento.servicos)
            .selectinload(TratamentoServico.servico),
            selectinload(tratamentos.Tratamento.servicos)
            .selectinload(TratamentoServico.academico),
            selectinload(tratamentos.Tratamento.servicos)
            .selectinload(TratamentoServico.monitor),
        )
        .filter(
            tratamentos.Tratamento.id == tratamento_id,
            tratamentos.Tratamento.tenant_id == tenant_id,
        )
    )
    result = await db.execute(query)
    return result.scalars().first()


async def get_tratamentos(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    paciente_id: Optional[uuid.UUID] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[tratamentos.Tratamento]:
    query = (
        select(tratamentos.Tratamento)
        .options(
            selectinload(tratamentos.Tratamento.servicos)
            .selectinload(TratamentoServico.servico),
            selectinload(tratamentos.Tratamento.servicos)
            .selectinload(TratamentoServico.academico),
            selectinload(tratamentos.Tratamento.servicos)
            .selectinload(TratamentoServico.monitor),
        )
        .filter(tratamentos.Tratamento.tenant_id == tenant_id)
    )

    if paciente_id is not None:
        query = query.filter(tratamentos.Tratamento.paciente_id == paciente_id)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def create_tratamento(
    db: AsyncSession,
    tratamento: schemas.TratamentoCreate,
    tenant_id: uuid.UUID,
):
    # Check for patient consent before creating treatment
    if tratamento.paciente_id:
        consents = await consent_crud.get_consentimentos_by_paciente(db=db, paciente_id=tratamento.paciente_id, tenant_id=tenant_id)
        valid_consent_found = False
        for consent in consents:
            if consent.tipo_consentimento == 'Tratamento Geral' and \
               consent.data_consentimento > datetime.datetime.now() - datetime.timedelta(days=365):
                valid_consent_found = True
                break
        if not valid_consent_found:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Paciente não possui um consentimento válido e ativo para iniciar o tratamento."
            )

    if tratamento.paciente_id is None:
        existing_tratamento_query = select(tratamentos.Tratamento).filter(
            and_(
                tratamentos.Tratamento.nome == tratamento.nome,
                tratamentos.Tratamento.paciente_id.is_(None),
                tratamentos.Tratamento.tenant_id == tenant_id,
            )
        )
    else:
        existing_tratamento_query = select(tratamentos.Tratamento).filter(
            and_(
                tratamentos.Tratamento.nome == tratamento.nome,
                tratamentos.Tratamento.paciente_id == tratamento.paciente_id,
                tratamentos.Tratamento.tenant_id == tenant_id,
            )
        )

    existing_tratamento_result = await db.execute(existing_tratamento_query)
    if existing_tratamento_result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Tratamento com este nome já existe para este paciente "
                "(ou como tratamento geral)."
            ),
        )

    db_tratamento = tratamentos.Tratamento(
        paciente_id=tratamento.paciente_id,
        nome=tratamento.nome,
        descricao=tratamento.descricao,
        status=tratamento.status,
        tenant_id=tenant_id,
    )
    db.add(db_tratamento)
    await db.flush()

    if getattr(tratamento, "servicos", None):
        for servico_data in tratamento.servicos:
            await tratamento_servicos_crud.add_servico_to_tratamento(
                db,
                tratamento_id=db_tratamento.id,
                servico_id=servico_data.servico_id,
                quantidade=1,  # default = 1
                tenant_id=tenant_id,
                academico_id=servico_data.academico_id,
                monitor_id=servico_data.monitor_id,
            )

    await db.commit()
    await db.refresh(db_tratamento)
    return await get_tratamento(db, tratamento_id=db_tratamento.id, tenant_id=tenant_id)


async def update_tratamento(
    db: AsyncSession,
    tratamento_id: uuid.UUID,
    tratamento_data: schemas.TratamentoUpdate,
    tenant_id: uuid.UUID,
):
    result = await db.execute(
        select(tratamentos.Tratamento).filter(
            tratamentos.Tratamento.id == tratamento_id,
            tratamentos.Tratamento.tenant_id == tenant_id,
        )
    )
    db_tratamento = result.scalars().first()
    if not db_tratamento:
        return None

    update_dict = _model_to_dict(tratamento_data, exclude_unset=True, exclude={"servicos"})
    for key, value in update_dict.items():
        setattr(db_tratamento, key, value)

    if getattr(tratamento_data, "servicos", None) is not None:
        # Remove serviços atuais
        for existing_servico in list(db_tratamento.servicos or []):
            await db.delete(existing_servico)
        await db.flush()

        # Adiciona novos serviços
        for servico_data in tratamento_data.servicos:
            await tratamento_servicos_crud.add_servico_to_tratamento(
                db,
                tratamento_id=db_tratamento.id,
                servico_id=servico_data.servico_id,
                quantidade=1,  # default = 1
                tenant_id=tenant_id,
                academico_id=servico_data.academico_id,
                monitor_id=servico_data.monitor_id,
            )

    await db.commit()
    await db.refresh(db_tratamento)
    return await get_tratamento(db, tratamento_id=db_tratamento.id, tenant_id=tenant_id)


async def delete_tratamento(
    db: AsyncSession,
    tratamento_id: uuid.UUID,
    tenant_id: uuid.UUID,
):
    db_tratamento_to_return = await get_tratamento(
        db, tratamento_id=tratamento_id, tenant_id=tenant_id
    )
    if db_tratamento_to_return:
        await db.delete(db_tratamento_to_return)
        await db.commit()
    return db_tratamento_to_return


async def cancelar_tratamento(
    db: AsyncSession, tratamento_id: uuid.UUID, tenant_id: uuid.UUID
):
    db_tratamento = await get_tratamento(
        db, tratamento_id=tratamento_id, tenant_id=tenant_id
    )
    if not db_tratamento:
        return None

    db_tratamento.status = tratamentos.TreatmentStatus.cancelado
    await db.commit()
    await db.refresh(db_tratamento)
    return db_tratamento


async def ativar_tratamento(
    db: AsyncSession, tratamento_id: uuid.UUID, tenant_id: uuid.UUID
):
    db_tratamento = await get_tratamento(
        db, tratamento_id=tratamento_id, tenant_id=tenant_id
    )
    if not db_tratamento:
        return None

    db_tratamento.status = tratamentos.TreatmentStatus.em_progresso
    await db.commit()
    await db.refresh(db_tratamento)
    return db_tratamento


async def finalizar_tratamento(
    db: AsyncSession, tratamento_id: uuid.UUID, tenant_id: uuid.UUID
):
    db_tratamento = await get_tratamento(
        db, tratamento_id=tratamento_id, tenant_id=tenant_id
    )
    if not db_tratamento:
        return None

    db_tratamento.status = tratamentos.TreatmentStatus.concluido

    # Coleta de dados para o PDF
    tenant_result = await db.execute(
        select(tenant_models.Tenant).filter(tenant_models.Tenant.id == tenant_id)
    )
    tenant = tenant_result.scalars().first()

    paciente_result = await db.execute(
        select(paciente_models.Paciente).filter(
            paciente_models.Paciente.id == db_tratamento.paciente_id
        )
    )
    paciente = paciente_result.scalars().first()

    agendamentos = await agendamentos_crud.get_agendamentos(
        db, tenant_id=tenant_id, tratamento_id=tratamento_id
    )

    # Montagem dos serviços realizados
    servicos_details = []
    for servico_tratamento in (db_tratamento.servicos or []):
        servico_agendamentos = [
            ag for ag in agendamentos if ag.servico_id == servico_tratamento.servico_id
        ]
        for agendamento in servico_agendamentos:
            academico = None
            monitor = None
            if agendamento.academico_id:
                academico_result = await db.execute(
                    select(user_models.SystemUser).filter(
                        user_models.SystemUser.id == agendamento.academico_id
                    )
                )
                academico = academico_result.scalars().first()
            if agendamento.monitor_id:
                monitor_result = await db.execute(
                    select(user_models.SystemUser).filter(
                        user_models.SystemUser.id == agendamento.monitor_id
                    )
                )
                monitor = monitor_result.scalars().first()

            servicos_details.append(
                {
                    "nome": getattr(servico_tratamento.servico, "nome", "N/A"),
                    "data": (
                        agendamento.start_time.strftime("%d/%m/%Y %H:%M")
                        if getattr(agendamento, "start_time", None)
                        else "N/A"
                    ),
                    "academico": getattr(academico, "nome", "N/A"),
                    "monitor": getattr(monitor, "nome", "N/A"),
                }
            )

    # Template HTML do relatório
    template_str = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset=\"utf-8\" />
        <title>Relatório de Tratamento</title>
        <style>
            body { font-family: sans-serif; }
            h1, h2 { text-align: center; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #dddddd; text-align: left; padding: 8px; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h1>Relatório de Tratamento</h1>
        <h2>{{ tratamento_nome }}</h2>
        <p><strong>Clínica:</strong> {{ tenant_name }}</p>
        <p><strong>Paciente:</strong> {{ paciente_name }}</p>
        <p><strong>Data de Finalização:</strong> {{ data_finalizacao }}</p>
        <h3>Serviços Realizados</h3>
        <table>
            <tr>
                <th>Serviço</th>
                <th>Data e Hora</th>
                <th>Acadêmico</th>
                <th>Monitor</th>
            </tr>
            {% for servico in servicos %}
            <tr>
                <td>{{ servico.nome }}</td>
                <td>{{ servico.data }}</td>
                <td>{{ servico.academico }}</td>
                <td>{{ servico.monitor }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """

    template = jinja2.Template(template_str)
    html_content = template.render(
        tratamento_nome=db_tratamento.nome,
        tenant_name=getattr(tenant, "nome", "N/A"),
        paciente_name=getattr(paciente, "nome", "N/A"),
        data_finalizacao=datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        servicos=servicos_details,
    )

    # Armazenamento do PDF
    base_path = os.path.join("storage", _sanitize_dirname(getattr(tenant, "nome", None)), "prontuario")
    os.makedirs(base_path, exist_ok=True)

    dir_count = 1
    while True:
        dir_path = os.path.join(base_path, f"{dir_count:04d}")
        # Pasta nova ou com menos de 400 arquivos
        if not os.path.exists(dir_path) or len(os.listdir(dir_path)) < 400:
            break
        dir_count += 1

    os.makedirs(dir_path, exist_ok=True)

    pdf_file_name = f"tratamento_{db_tratamento.id}.pdf"
    pdf_file_path = os.path.join(dir_path, pdf_file_name)

    # Geração de PDF (pode falhar se dependências de sistema do WeasyPrint não estiverem presentes)
    try:
        with open(pdf_file_path, "wb") as f:
            pisa.CreatePDF(html_content, dest=f)
    except Exception as e:
        # Em produção, troque por log apropriado
        # Não interrompe a finalização do tratamento
        print(f"Falha ao gerar PDF: {e}")

    await db.commit()
    await db.refresh(db_tratamento)
    return db_tratamento
