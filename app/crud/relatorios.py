import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, cast, Date
from datetime import datetime

from ..models import agendamentos as agendamento_models, users as user_models, servicos as servico_models, prontuarios as prontuario_models, tratamentos as tratamento_models, planos_custo as plano_custo_models, pacientes as paciente_models
from ..schemas import relatorios as schemas

async def get_horas_atendimento_academico(db: AsyncSession, tenant_id: uuid.UUID, start_date: datetime, end_date: datetime) -> schemas.RelatorioHorasAtendimento:
    # Ensure dates are naive for comparison with TIMESTAMP columns
    start_date = start_date.replace(tzinfo=None)
    end_date = end_date.replace(tzinfo=None)

    result = await db.execute(
        select(
            user_models.SystemUser.id,
            user_models.SystemUser.nome,
            func.sum(func.extract('epoch', agendamento_models.Agendamento.fim - agendamento_models.Agendamento.inicio) / 3600).label('total_horas')
        )
        .join(user_models.SystemUser, agendamento_models.Agendamento.profissional_id == user_models.SystemUser.id)
        .filter(
            agendamento_models.Agendamento.tenant_id == tenant_id,
            agendamento_models.Agendamento.status == agendamento_models.AppointmentStatus.concluido, # Only count concluded appointments
            agendamento_models.Agendamento.inicio >= start_date,
            agendamento_models.Agendamento.fim <= end_date
        )
        .group_by(user_models.SystemUser.id, user_models.SystemUser.nome)
        .order_by(user_models.SystemUser.nome)
    )
    
    report_data = []
    for row in result.all():
        report_data.append(schemas.HorasAtendimentoAcademico(
            profissional_id=row.id,
            nome_profissional=row.nome,
            total_horas=round(row.total_horas, 2) if row.total_horas else 0.0
        ))

    return schemas.RelatorioHorasAtendimento(
        data_inicio=start_date.isoformat(),
        data_fim=end_date.isoformat(),
        relatorio=report_data
    )

async def get_procedimentos_por_estudante(db: AsyncSession, tenant_id: uuid.UUID, start_date: datetime, end_date: datetime) -> schemas.RelatorioProcedimentosPorEstudante:
    start_date = start_date.replace(tzinfo=None)
    end_date = end_date.replace(tzinfo=None)

    result = await db.execute(
        select(
            user_models.SystemUser.id,
            user_models.SystemUser.nome,
            servico_models.Servico.nome.label('servico_nome'),
            func.count(agendamento_models.Agendamento.id).label('quantidade')
        )
        .join(user_models.SystemUser, agendamento_models.Agendamento.profissional_id == user_models.SystemUser.id)
        .join(servico_models.Servico, agendamento_models.Agendamento.servico_id == servico_models.Servico.id)
        .filter(
            agendamento_models.Agendamento.tenant_id == tenant_id,
            agendamento_models.Agendamento.status == agendamento_models.AppointmentStatus.concluido, # Only count concluded appointments
            agendamento_models.Agendamento.inicio >= start_date,
            agendamento_models.Agendamento.fim <= end_date
        )
        .group_by(user_models.SystemUser.id, user_models.SystemUser.nome, servico_models.Servico.nome)
        .order_by(user_models.SystemUser.nome, servico_models.Servico.nome)
    )

    report_data_raw = result.all()
    
    # Group by student
    grouped_data = {}
    for row in report_data_raw:
        if row.id not in grouped_data:
            grouped_data[row.id] = {
                "profissional_id": row.id,
                "nome_profissional": row.nome,
                "procedimentos": []
            }
        grouped_data[row.id]["procedimentos"].append(schemas.ProcedimentoPorTipo(
            servico_nome=row.servico_nome,
            quantidade=row.quantidade
        ))
    
    report_data = [schemas.ProcedimentosPorEstudante(**data) for data in grouped_data.values()]

    return schemas.RelatorioProcedimentosPorEstudante(
        data_inicio=start_date.isoformat(),
        data_fim=end_date.isoformat(),
        relatorio=report_data
    )

async def get_tempo_medio_aprovacao_prontuarios(db: AsyncSession, tenant_id: uuid.UUID, start_date: datetime, end_date: datetime) -> schemas.RelatorioTempoMedioAprovacao:
    start_date = start_date.replace(tzinfo=None)
    end_date = end_date.replace(tzinfo=None)

    result = await db.execute(
        select(
            user_models.SystemUser.id,
            user_models.SystemUser.nome,
            func.avg(func.extract('epoch', prontuario_models.Prontuario.updated_at - prontuario_models.Prontuario.created_at) / 3600).label('tempo_medio_horas')
        )
        .join(user_models.SystemUser, prontuario_models.Prontuario.orientador_id == user_models.SystemUser.id)
        .filter(
            prontuario_models.Prontuario.tenant_id == tenant_id,
            prontuario_models.Prontuario.status_revisao == prontuario_models.ReviewStatus.aprovado, # Only count approved prontuarios
            prontuario_models.Prontuario.created_at >= start_date,
            prontuario_models.Prontuario.updated_at <= end_date
        )
        .group_by(user_models.SystemUser.id, user_models.SystemUser.nome)
        .order_by(user_models.SystemUser.nome)
    )

    report_data = []
    for row in result.all():
        report_data.append(schemas.TempoMedioAprovacaoOrientador(
            orientador_id=row.id,
            nome_orientador=row.nome,
            tempo_medio_aprovacao_horas=round(row.tempo_medio_horas, 2) if row.tempo_medio_horas else 0.0
        ))

    return schemas.RelatorioTempoMedioAprovacao(
        data_inicio=start_date.isoformat(),
        data_fim=end_date.isoformat(),
        relatorio=report_data
    )

async def get_visao_geral_agendamentos(db: AsyncSession, tenant_id: uuid.UUID, start_date: datetime, end_date: datetime) -> schemas.VisaoGeralAgendamentos:
    start_date = start_date.replace(tzinfo=None)
    end_date = end_date.replace(tzinfo=None)

    # Total appointments
    total_agendamentos_result = await db.execute(
        select(func.count(agendamento_models.Agendamento.id))
        .filter(
            agendamento_models.Agendamento.tenant_id == tenant_id,
            agendamento_models.Agendamento.inicio >= start_date,
            agendamento_models.Agendamento.fim <= end_date
        )
    )
    total_agendamentos = total_agendamentos_result.scalar_one()

    # Appointments by status
    agendamentos_por_status_result = await db.execute(
        select(
            agendamento_models.Agendamento.status,
            func.count(agendamento_models.Agendamento.id)
        )
        .filter(
            agendamento_models.Agendamento.tenant_id == tenant_id,
            agendamento_models.Agendamento.inicio >= start_date,
            agendamento_models.Agendamento.fim <= end_date
        )
        .group_by(agendamento_models.Agendamento.status)
    )
    agendamentos_por_status = [
        schemas.AgendamentosPorStatus(status=row.status.value, quantidade=row.count)
        for row in agendamentos_por_status_result.all()
    ]

    # Appointments by professional
    agendamentos_por_profissional_result = await db.execute(
        select(
            user_models.SystemUser.id,
            user_models.SystemUser.nome,
            func.count(agendamento_models.Agendamento.id)
        )
        .join(user_models.SystemUser, agendamento_models.Agendamento.profissional_id == user_models.SystemUser.id)
        .filter(
            agendamento_models.Agendamento.tenant_id == tenant_id,
            agendamento_models.Agendamento.inicio >= start_date,
            agendamento_models.Agendamento.fim <= end_date
        )
        .group_by(user_models.SystemUser.id, user_models.SystemUser.nome)
        .order_by(user_models.SystemUser.nome)
    )
    agendamentos_por_profissional = [
        schemas.AgendamentosPorProfissional(profissional_id=row.id, nome_profissional=row.nome, quantidade=row.count)
        for row in agendamentos_por_profissional_result.all()
    ]

    # Appointments by service
    agendamentos_por_servico_result = await db.execute(
        select(
            servico_models.Servico.id,
            servico_models.Servico.nome,
            func.count(agendamento_models.Agendamento.id)
        )
        .join(servico_models.Servico, agendamento_models.Agendamento.servico_id == servico_models.Servico.id)
        .filter(
            agendamento_models.Agendamento.tenant_id == tenant_id,
            agendamento_models.Agendamento.inicio >= start_date,
            agendamento_models.Agendamento.fim <= end_date
        )
        .group_by(servico_models.Servico.id, servico_models.Servico.nome)
        .order_by(servico_models.Servico.nome)
    )
    agendamentos_por_servico = [
        schemas.AgendamentosPorServico(servico_id=row.id, nome_servico=row.nome, quantidade=row.count)
        for row in agendamentos_por_servico_result.all()
    ]

    return schemas.VisaoGeralAgendamentos(
        data_inicio=start_date.isoformat(),
        data_fim=end_date.isoformat(),
        total_agendamentos=total_agendamentos,
        agendamentos_por_status=agendamentos_por_status,
        agendamentos_por_profissional=agendamentos_por_profissional,
        agendamentos_por_servico=agendamentos_por_servico
    )

async def get_tratamentos_por_status(db: AsyncSession, tenant_id: uuid.UUID, start_date: datetime, end_date: datetime) -> schemas.RelatorioTratamentosPorStatus:
    start_date = start_date.replace(tzinfo=None)
    end_date = end_date.replace(tzinfo=None)

    result = await db.execute(
        select(
            tratamento_models.Tratamento.status,
            func.count(tratamento_models.Tratamento.id)
        )
        .filter(
            tratamento_models.Tratamento.tenant_id == tenant_id,
            tratamento_models.Tratamento.created_at >= start_date,
            tratamento_models.Tratamento.created_at <= end_date
        )
        .group_by(tratamento_models.Tratamento.status)
    )

    report_data = [
        schemas.TratamentosPorStatus(status=row.status.value, quantidade=row.count)
        for row in result.all()
    ]

    return schemas.RelatorioTratamentosPorStatus(
        data_inicio=start_date.isoformat(),
        data_fim=end_date.isoformat(),
        relatorio=report_data
    )

async def get_resumo_financeiro(db: AsyncSession, tenant_id: uuid.UUID, start_date: datetime, end_date: datetime) -> schemas.ResumoFinanceiro:
    start_date = start_date.replace(tzinfo=None)
    end_date = end_date.replace(tzinfo=None)

    # Total planos_custo
    total_planos_custo_result = await db.execute(
        select(func.count(plano_custo_models.PlanoCusto.id))
        .filter(
            plano_custo_models.PlanoCusto.tenant_id == tenant_id,
            plano_custo_models.PlanoCusto.created_at >= start_date,
            plano_custo_models.PlanoCusto.created_at <= end_date
        )
    )
    total_planos_custo = total_planos_custo_result.scalar_one()

    # Total valor by status
    total_valor_aprovado_result = await db.execute(
        select(func.sum(plano_custo_models.PlanoCusto.valor_total))
        .filter(
            plano_custo_models.PlanoCusto.tenant_id == tenant_id,
            plano_custo_models.PlanoCusto.status == plano_custo_models.PlanoCustoStatus.aprovado,
            plano_custo_models.PlanoCusto.created_at >= start_date,
            plano_custo_models.PlanoCusto.created_at <= end_date
        )
    )
    total_valor_aprovado = total_valor_aprovado_result.scalar_one() or 0.0

    total_valor_pendente_result = await db.execute(
        select(func.sum(plano_custo_models.PlanoCusto.valor_total))
        .filter(
            plano_custo_models.PlanoCusto.tenant_id == tenant_id,
            plano_custo_models.PlanoCusto.status == plano_custo_models.PlanoCustoStatus.pendente,
            plano_custo_models.PlanoCusto.created_at >= start_date,
            plano_custo_models.PlanoCusto.created_at <= end_date
        )
    )
    total_valor_pendente = total_valor_pendente_result.scalar_one() or 0.0

    total_valor_cancelado_result = await db.execute(
        select(func.sum(plano_custo_models.PlanoCusto.valor_total))
        .filter(
            plano_custo_models.PlanoCusto.tenant_id == tenant_id,
            plano_custo_models.PlanoCusto.status == plano_custo_models.PlanoCustoStatus.cancelado,
            plano_custo_models.PlanoCusto.created_at >= start_date,
            plano_custo_models.PlanoCusto.created_at <= end_date
        )
    )
    total_valor_cancelado = total_valor_cancelado_result.scalar_one() or 0.0

    return schemas.ResumoFinanceiro(
        data_inicio=start_date.isoformat(),
        data_fim=end_date.isoformat(),
        total_planos_custo=total_planos_custo,
        total_valor_aprovado=float(total_valor_aprovado),
        total_valor_pendente=float(total_valor_pendente),
        total_valor_cancelado=float(total_valor_cancelado)
    )

async def get_custos_tratamento_por_periodo(db: AsyncSession, tenant_id: uuid.UUID, start_date: datetime, end_date: datetime) -> schemas.RelatorioCustosTratamento:
    start_date = start_date.replace(tzinfo=None)
    end_date = end_date.replace(tzinfo=None)

    # Fetch treatments within the period
    treatments_query = select(
        tratamento_models.Tratamento,
        paciente_models.Paciente.nome.label('nome_paciente')
    ).join(
        paciente_models.Paciente, tratamento_models.Tratamento.paciente_id == paciente_models.Paciente.id
    ).filter(
        tratamento_models.Tratamento.tenant_id == tenant_id,
        tratamento_models.Tratamento.created_at >= start_date,
        tratamento_models.Tratamento.created_at <= end_date
    )
    treatments_result = await db.execute(treatments_query)
    treatments = treatments_result.scalars().all()

    report_data = []
    total_geral_custos = 0.0

    for tratamento in treatments:
        # Fetch services associated with each treatment
        servicos_tratamento_query = select(
            servico_models.Servico.nome.label('servico_nome'),
            servico_models.Servico.custo.label('custo')
        ).join(
            tratamento_models.TratamentoServico, tratamento_models.TratamentoServico.servico_id == servico_models.Servico.id
        ).filter(
            tratamento_models.TratamentoServico.tratamento_id == tratamento.id
        )
        servicos_tratamento_result = await db.execute(servicos_tratamento_query)
        servicos_incluidos = [
            schemas.CustoServicoTratamento(servico_nome=row.servico_nome, custo=float(row.custo))
            for row in servicos_tratamento_result.all()
        ]

        custo_total_tratamento = sum(s.custo for s in servicos_incluidos)
        total_geral_custos += custo_total_tratamento

        report_data.append(schemas.CustoTratamento(
            tratamento_id=tratamento.id,
            nome_tratamento=tratamento.descricao, # Assuming descricao is the treatment name
            nome_paciente=tratamento.nome_paciente,
            custo_total_tratamento=float(custo_total_tratamento),
            servicos_incluidos=servicos_incluidos
        ))

    return schemas.RelatorioCustosTratamento(
        data_inicio=start_date.isoformat(),
        data_fim=end_date.isoformat(),
        relatorio=report_data,
        total_geral_custos=float(total_geral_custos)
    )