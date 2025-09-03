import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from fastapi import HTTPException, status
from ..models import agendamentos as models, pacientes as paciente_models
from ..schemas import agendamentos as agendamentos_schemas
from ..services.notification_service import NotificationService
from typing import Optional
from sqlalchemy.orm import joinedload, selectinload
from ..models.tratamentos import Tratamento
from ..models.tratamento_servicos import TratamentoServico
from datetime import datetime, date
import jinja2
from xhtml2pdf import pisa
from ..models import tenants as tenant_models

async def get_agendamento(db: AsyncSession, agendamento_id: uuid.UUID, tenant_id: uuid.UUID):
    result = await db.execute(
        select(models.Agendamento)
        .options(
            joinedload(models.Agendamento.paciente),
            joinedload(models.Agendamento.academico),
            joinedload(models.Agendamento.orientador),
            joinedload(models.Agendamento.tratamento).selectinload(Tratamento.servicos).joinedload(TratamentoServico.servico),
            joinedload(models.Agendamento.servico)
        )
        .filter(models.Agendamento.id == agendamento_id, models.Agendamento.tenant_id == tenant_id)
    )
    return result.scalars().first()

async def get_agendamentos(
    db: AsyncSession,
    tenant_id: Optional[uuid.UUID],
    academico_id: Optional[uuid.UUID] = None,
    orientador_id: Optional[uuid.UUID] = None,
    servico_id: Optional[uuid.UUID] = None,
    date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100
):
    stmt = select(models.Agendamento).options(
        joinedload(models.Agendamento.paciente),
        joinedload(models.Agendamento.academico),
        joinedload(models.Agendamento.orientador),
        joinedload(models.Agendamento.tratamento).selectinload(Tratamento.servicos).joinedload(TratamentoServico.servico),
        joinedload(models.Agendamento.servico)
    )
    if tenant_id is not None:
        stmt = stmt.filter(models.Agendamento.tenant_id == tenant_id)
    
    if academico_id is not None:
        stmt = stmt.filter(models.Agendamento.academico_id == academico_id)

    if orientador_id is not None:
        stmt = stmt.filter(models.Agendamento.orientador_id == orientador_id)
    
    if servico_id is not None:
        stmt = stmt.filter(models.Agendamento.servico_id == servico_id)

    if date is not None:
        start_of_day = datetime.combine(date, datetime.min.time())
        end_of_day = datetime.combine(date, datetime.max.time())
        stmt = stmt.filter(models.Agendamento.inicio >= start_of_day, models.Agendamento.inicio <= end_of_day)

    result = await db.execute(stmt.offset(skip).limit(limit))
    agendamentos = result.scalars().all()

    # Não fazer expunge para manter os relacionamentos carregados
    return agendamentos

async def create_agendamento(db: AsyncSession, agendamento: agendamentos_schemas.AgendamentoCreate, tenant_id: uuid.UUID):
    if agendamento.inicio.tzinfo is not None:
        agendamento.inicio = agendamento.inicio.replace(tzinfo=None)
    if agendamento.fim.tzinfo is not None:
        agendamento.fim = agendamento.fim.replace(tzinfo=None)

    overlapping_appointments = await db.execute(
        select(models.Agendamento).filter(
            and_(
                models.Agendamento.academico_id == agendamento.academico_id,
                models.Agendamento.tenant_id == tenant_id,
                models.Agendamento.fim > agendamento.inicio,
                models.Agendamento.inicio < agendamento.fim
            )
        )
    )
    if overlapping_appointments.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Appointment overlaps with an existing appointment for this academic."
        )

    db_agendamento = models.Agendamento(
        **agendamento.model_dump(exclude_unset=True),
        tenant_id=tenant_id
    )
    db.add(db_agendamento)
    # No db.commit() or db.refresh() here. Commit after reload.

    # Recarregar o agendamento com os relacionamentos carregados
    result = await db.execute(
        select(models.Agendamento)
        .options(
            joinedload(models.Agendamento.paciente),
            joinedload(models.Agendamento.academico),
            joinedload(models.Agendamento.orientador),
            joinedload(models.Agendamento.tratamento).selectinload(Tratamento.servicos).joinedload(TratamentoServico.servico),
            joinedload(models.Agendamento.servico)
        )
        .filter(models.Agendamento.id == db_agendamento.id)
    )
    db_agendamento = result.scalars().first()
    await db.commit() # Commit after the object is fully loaded

    if db_agendamento.status == models.AppointmentStatus.agendado:
        paciente = await db.execute(select(paciente_models.Paciente).filter_by(id=db_agendamento.paciente_id, tenant_id=tenant_id))
        db_paciente = paciente.scalars().first()
        if db_paciente and db_paciente.email:
            notification_service = NotificationService(db)
            subject = f"Lembrete de Agendamento: {db_agendamento.servico_id}"
            body = f"""Olá {db_paciente.nome},

Este é um lembrete do seu agendamento para {db_agendamento.servico_id} em {db_agendamento.inicio.strftime('%d/%m/%Y %H:%M')}.

Atenciosamente,
Sua Clínica"""
            await notification_service.send_email(tenant_id, db_paciente.email, subject, body)

    return db_agendamento

async def update_agendamento(db: AsyncSession, agendamento_id: uuid.UUID, agendamento_data: agendamentos_schemas.AgendamentoUpdate, tenant_id: uuid.UUID):
    result = await db.execute(select(models.Agendamento).filter(models.Agendamento.id == agendamento_id, models.Agendamento.tenant_id == tenant_id))
    db_agendamento = result.scalars().first()
    if not db_agendamento:
        return None

    update_data = agendamento_data.model_dump(exclude_unset=True)

    # Overlap check logic
    if 'inicio' in update_data or 'fim' in update_data or 'academico_id' in update_data:
        new_inicio = update_data.get('inicio', db_agendamento.inicio)
        new_fim = update_data.get('fim', db_agendamento.fim)
        academico_id = update_data.get('academico_id', db_agendamento.academico_id)

        if hasattr(new_inicio, 'tzinfo') and new_inicio.tzinfo is not None:
            new_inicio = new_inicio.replace(tzinfo=None)
        if hasattr(new_fim, 'tzinfo') and new_fim.tzinfo is not None:
            new_fim = new_fim.replace(tzinfo=None)

        overlapping_appointments = await db.execute(
            select(models.Agendamento).filter(
                and_(
                    models.Agendamento.id != agendamento_id,
                    models.Agendamento.academico_id == academico_id,
                    models.Agendamento.tenant_id == tenant_id,
                    models.Agendamento.fim > new_inicio,
                    models.Agendamento.inicio < new_fim
                )
            )
        )
        if overlapping_appointments.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Appointment overlaps with an existing appointment for this academic."
            )

    # Update attributes
    for key, value in update_data.items():
        if (key == 'inicio' or key == 'fim') and hasattr(value, 'tzinfo') and value.tzinfo is not None:
            value = value.replace(tzinfo=None)
        setattr(db_agendamento, key, value)
    
    # No db.commit() or db.refresh() here. Commit after reload.

    # Recarregar o agendamento com os relacionamentos carregados
    result = await db.execute(
        select(models.Agendamento)
        .options(
            joinedload(models.Agendamento.paciente),
            joinedload(models.Agendamento.academico),
            joinedload(models.Agendamento.orientador),
            joinedload(models.Agendamento.tratamento).selectinload(Tratamento.servicos).joinedload(TratamentoServico.servico),
            joinedload(models.Agendamento.servico)
        )
        .filter(models.Agendamento.id == db_agendamento.id)
    )
    db_agendamento = result.scalars().first()
    await db.commit() # Commit after the object is fully loaded

    if db_agendamento.status == models.AppointmentStatus.agendado:
        paciente = await db.execute(select(paciente_models.Paciente).filter_by(id=db_agendamento.paciente_id, tenant_id=tenant_id))
        db_paciente = paciente.scalars().first()
        if db_paciente and db_paciente.email:
            notification_service = NotificationService(db)
            subject = f"Lembrete de Agendamento Atualizado: {db_agendamento.servico_id}"
            body = f"""Olá {db_paciente.nome},

Seu agendamento para {db_agendamento.servico_id} foi atualizado para {db_agendamento.inicio.strftime('%d/%m/%Y %H:%M')}.

Atenciosamente,
Sua Clínica"""
            await notification_service.send_email(tenant_id, db_paciente.email, subject, body)

    return db_agendamento

async def delete_agendamento(db: AsyncSession, agendamento_id: uuid.UUID, tenant_id: uuid.UUID):
    result = await db.execute(select(models.Agendamento).filter(models.Agendamento.id == agendamento_id, models.Agendamento.tenant_id == tenant_id))
    db_agendamento = result.scalars().first()
    if db_agendamento:
        await db.delete(db_agendamento)
        await db.commit()
    return db_agendamento

async def get_agendamentos_detalhes(db: AsyncSession, tenant_id: uuid.UUID, skip: int = 0, limit: int = 100):
    query = select(models.AgendamentoDetalhesView).filter(models.AgendamentoDetalhesView.tenant_id == tenant_id).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_agendamentos_by_paciente(
    db: AsyncSession,
    paciente_id: uuid.UUID,
    tenant_id: Optional[uuid.UUID] = None,
    skip: int = 0,
    limit: int = 100
):
    stmt = select(models.Agendamento).options(
        joinedload(models.Agendamento.paciente),
        joinedload(models.Agendamento.academico),
        joinedload(models.Agendamento.orientador),
        joinedload(models.Agendamento.tratamento).selectinload(Tratamento.servicos).joinedload(TratamentoServico.servico),
        joinedload(models.Agendamento.servico)
    ).filter(models.Agendamento.paciente_id == paciente_id)
    
    if tenant_id is not None:
        stmt = stmt.filter(models.Agendamento.tenant_id == tenant_id)

    result = await db.execute(stmt.offset(skip).limit(limit))
    agendamentos = result.scalars().all()

    # Não fazer expunge para manter os relacionamentos carregados
    return agendamentos

async def iniciar_atendimento(
    db: AsyncSession, 
    agendamento_id: uuid.UUID, 
    tenant_id: uuid.UUID
):
    """Inicia um atendimento, marcando o horário de início"""
    result = await db.execute(
        select(models.Agendamento).filter(
            models.Agendamento.id == agendamento_id, 
            models.Agendamento.tenant_id == tenant_id
        )
    )
    db_agendamento = result.scalars().first()
    if not db_agendamento:
        return None
    
    db_agendamento.status = models.AppointmentStatus.iniciado
    db_agendamento.hora_inicio_atendimento = datetime.datetime.now()
    await db.commit()
    await db.refresh(db_agendamento)
    
    # Recarregar os relacionamentos após o commit
    result = await db.execute(
        select(models.Agendamento).options(
            joinedload(models.Agendamento.paciente),
            joinedload(models.Agendamento.academico),
            joinedload(models.Agendamento.orientador),
            joinedload(models.Agendamento.tratamento).selectinload(Tratamento.servicos).joinedload(TratamentoServico.servico),
            joinedload(models.Agendamento.servico)
        ).filter(models.Agendamento.id == agendamento_id)
    )
    db_agendamento = result.scalars().first()
    
    return db_agendamento

async def aguardar_atendimento(
    db: AsyncSession, 
    agendamento_id: uuid.UUID, 
    tenant_id: uuid.UUID
):
    """Marca um atendimento como aguardando"""
    result = await db.execute(
        select(models.Agendamento).filter(
            models.Agendamento.id == agendamento_id, 
            models.Agendamento.tenant_id == tenant_id
        )
    )
    db_agendamento = result.scalars().first()
    if not db_agendamento:
        return None
    
    db_agendamento.status = models.AppointmentStatus.aguardando
    await db.commit()
    await db.refresh(db_agendamento)
    
    # Recarregar os relacionamentos após o commit
    result = await db.execute(
        select(models.Agendamento).options(
            joinedload(models.Agendamento.paciente),
            joinedload(models.Agendamento.academico),
            joinedload(models.Agendamento.orientador),
            joinedload(models.Agendamento.tratamento).selectinload(Tratamento.servicos).joinedload(TratamentoServico.servico),
            joinedload(models.Agendamento.servico)
        ).filter(models.Agendamento.id == agendamento_id)
    )
    db_agendamento = result.scalars().first()
    
    return db_agendamento

async def em_atendimento(
    db: AsyncSession, 
    agendamento_id: uuid.UUID, 
    tenant_id: uuid.UUID
):
    """Marca um atendimento como em andamento"""
    result = await db.execute(
        select(models.Agendamento).filter(
            models.Agendamento.id == agendamento_id, 
            models.Agendamento.tenant_id == tenant_id
        )
    )
    db_agendamento = result.scalars().first()
    if not db_agendamento:
        return None
    
    db_agendamento.status = models.AppointmentStatus.em_atendimento
    await db.commit()
    await db.refresh(db_agendamento)
    
    # Recarregar os relacionamentos após o commit
    result = await db.execute(
        select(models.Agendamento).options(
            joinedload(models.Agendamento.paciente),
            joinedload(models.Agendamento.academico),
            joinedload(models.Agendamento.orientador),
            joinedload(models.Agendamento.tratamento).selectinload(Tratamento.servicos).joinedload(TratamentoServico.servico),
            joinedload(models.Agendamento.servico)
        ).filter(models.Agendamento.id == agendamento_id)
    )
    db_agendamento = result.scalars().first()
    
    return db_agendamento

async def concluir_atendimento(
    db: AsyncSession, 
    agendamento_id: uuid.UUID, 
    tenant_id: uuid.UUID,
    observacoes: Optional[str] = None
):
    """Conclui um atendimento, marcando o horário de fim e gerando PDF"""
    result = await db.execute(
        select(models.Agendamento).options(
            joinedload(models.Agendamento.paciente),
            joinedload(models.Agendamento.academico),
            joinedload(models.Agendamento.orientador),
            joinedload(models.Agendamento.tratamento).selectinload(Tratamento.servicos).joinedload(TratamentoServico.servico),
            joinedload(models.Agendamento.servico)
        ).filter(
            models.Agendamento.id == agendamento_id, 
            models.Agendamento.tenant_id == tenant_id
        )
    )
    db_agendamento = result.scalars().first()
    if not db_agendamento:
        return None
    
    db_agendamento.status = models.AppointmentStatus.concluido
    db_agendamento.hora_fim_atendimento = datetime.datetime.now()
    if observacoes:
        db_agendamento.observacoes = observacoes
    
    # Gerar PDF do atendimento
    await gerar_pdf_atendimento(db, db_agendamento, tenant_id)
    
    await db.commit()
    await db.refresh(db_agendamento)
    
    # Recarregar os relacionamentos após o commit
    result = await db.execute(
        select(models.Agendamento).options(
            joinedload(models.Agendamento.paciente),
            joinedload(models.Agendamento.academico),
            joinedload(models.Agendamento.orientador),
            joinedload(models.Agendamento.tratamento).selectinload(Tratamento.servicos).joinedload(TratamentoServico.servico),
            joinedload(models.Agendamento.servico)
        ).filter(models.Agendamento.id == agendamento_id)
    )
    db_agendamento = result.scalars().first()
    
    return db_agendamento

async def gerar_pdf_atendimento(
    db: AsyncSession, 
    agendamento: models.Agendamento, 
    tenant_id: uuid.UUID
):
    """Gera PDF do atendimento e salva no storage"""
    try:
        # Buscar informações do tenant
        tenant_result = await db.execute(
            select(tenant_models.Tenant).filter(tenant_models.Tenant.id == tenant_id)
        )
        tenant = tenant_result.scalars().first()
        
        # Template HTML do relatório de atendimento
        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8" />
            <title>Relatório de Atendimento</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1, h2 { text-align: center; color: #2c3e50; }
                .header { background-color: #ecf0f1; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
                .info-section { margin: 20px 0; }
                .info-row { display: flex; margin: 10px 0; }
                .info-label { font-weight: bold; width: 150px; }
                .info-value { flex: 1; }
                .observacoes { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
                .footer { text-align: center; margin-top: 30px; color: #7f8c8d; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Relatório de Atendimento</h1>
                <h2>{{ tenant_name }}</h2>
            </div>
            
            <div class="info-section">
                <div class="info-row">
                    <div class="info-label">Paciente:</div>
                    <div class="info-value">{{ paciente_nome }}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">Acadêmico:</div>
                    <div class="info-value">{{ academico_nome }}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">Orientador:</div>
                    <div class="info-value">{{ orientador_nome }}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">Serviço:</div>
                    <div class="info-value">{{ servico_nome }}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">Tratamento:</div>
                    <div class="info-value">{{ tratamento_nome }}</div>
                </div>
            </div>
            
            <div class="info-section">
                <div class="info-row">
                    <div class="info-label">Data Agendada:</div>
                    <div class="info-value">{{ data_agendada }}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">Hora Início:</div>
                    <div class="info-value">{{ hora_inicio }}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">Hora Fim:</div>
                    <div class="info-value">{{ hora_fim }}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">Duração:</div>
                    <div class="info-value">{{ duracao }}</div>
                </div>
            </div>
            
            {% if observacoes %}
            <div class="observacoes">
                <h3>Observações:</h3>
                <p>{{ observacoes }}</p>
            </div>
            {% endif %}
            
            <div class="footer">
                <p>Relatório gerado automaticamente em {{ data_geracao }}</p>
                <p>ID do Atendimento: {{ agendamento_id }}</p>
            </div>
        </body>
        </html>
        """
        
        # Calcular duração
        duracao = "N/A"
        if agendamento.hora_inicio_atendimento and agendamento.hora_fim_atendimento:
            diff = agendamento.hora_fim_atendimento - agendamento.hora_inicio_atendimento
            horas = diff.total_seconds() // 3600
            minutos = (diff.total_seconds() % 3600) // 60
            duracao = f"{int(horas)}h {int(minutos)}min"
        
        template = jinja2.Template(template_str)
        html_content = template.render(
            tenant_name=getattr(tenant, "nome", "N/A"),
            paciente_nome=getattr(agendamento.paciente, "nome", "N/A"),
            academico_nome=getattr(agendamento.academico, "nome", "N/A"),
            orientador_nome=getattr(agendamento.orientador, "nome", "N/A") if agendamento.orientador else "N/A",
            servico_nome=getattr(agendamento.servico, "nome", "N/A") if agendamento.servico else "N/A",
            tratamento_nome=getattr(agendamento.tratamento, "nome", "N/A") if agendamento.tratamento else "N/A",
            data_agendada=agendamento.inicio.strftime("%d/%m/%Y"),
            hora_inicio=agendamento.hora_inicio_atendimento.strftime("%H:%M") if agendamento.hora_inicio_atendimento else "N/A",
            hora_fim=agendamento.hora_fim_atendimento.strftime("%H:%M") if agendamento.hora_fim_atendimento else "N/A",
            duracao=duracao,
            observacoes=agendamento.observacoes or "",
            data_geracao=datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            agendamento_id=str(agendamento.id)
        )
        
        # Usar o sistema de storage existente
        from ..core.storage import get_storage_path
        
        # Nome do arquivo baseado no acadêmico e data
        nome_arquivo = f"atendimento_{getattr(agendamento.academico, 'nome', 'academico').replace(' ', '_')}_{agendamento.inicio.strftime('%Y%m%d_%H%M')}"
        
        # Obter caminho do storage
        file_path = get_storage_path(
            tenant_name=getattr(tenant, "nome", "tenant"),
            document_type="prontuarios",
            record_id=nome_arquivo,
            file_extension=".pdf"
        )
        
        # Gerar PDF
        with open(file_path, "wb") as f:
            pisa.CreatePDF(html_content, dest=f)
        
        # Salvar referência do documento no banco
        from ..models.documentos_paciente import DocumentoPaciente
        from ..schemas.documentos_paciente import DocumentoPacienteCreate
        
        documento_data = DocumentoPacienteCreate(
            paciente_id=agendamento.paciente_id,
            tipo="Relatório de Atendimento",
            arquivo_url=file_path,
            observacoes=f"Relatório do atendimento realizado em {agendamento.inicio.strftime('%d/%m/%Y')} pelo acadêmico {getattr(agendamento.academico, 'nome', 'N/A')}"
        )
        
        from ..crud.documentos_paciente import create_documento_paciente
        await create_documento_paciente(db, documento_data, tenant_id)
        
    except Exception as e:
        print(f"Erro ao gerar PDF do atendimento: {e}")
        # Não interrompe o fluxo principal