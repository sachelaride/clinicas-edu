
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import uuid

from ..crud import relatorios as crud
from ..schemas import relatorios as schemas
from ..db.database import get_db
from ..routes.auth import get_current_active_user
from ..models.users import SystemUser
from ..core.permissions import can_view_reports

router = APIRouter()

@router.get("/relatorios/horas-atendimento-academico", response_model=schemas.RelatorioHorasAtendimento, tags=["Relatórios"])
async def get_horas_atendimento_academico(
    start_date: datetime = Query(..., description="Data de início (YYYY-MM-DDTHH:MM:SS)"),
    end_date: datetime = Query(..., description="Data de fim (YYYY-MM-DDTHH:MM:SS)"),
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_view_reports)
):
    tenant_id = current_user.default_tenant_id
    return await crud.get_horas_atendimento_academico(db, tenant_id, start_date, end_date)

@router.get("/relatorios/procedimentos-por-estudante", response_model=schemas.RelatorioProcedimentosPorEstudante, tags=["Relatórios"])
async def get_procedimentos_por_estudante(
    start_date: datetime = Query(..., description="Data de início (YYYY-MM-DDTHH:MM:SS)"),
    end_date: datetime = Query(..., description="Data de fim (YYYY-MM-DDTHH:MM:SS)"),
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_view_reports)
):
    tenant_id = current_user.default_tenant_id
    return await crud.get_procedimentos_por_estudante(db, tenant_id, start_date, end_date)

@router.get("/relatorios/tempo-medio-aprovacao-prontuarios", response_model=schemas.RelatorioTempoMedioAprovacao, tags=["Relatórios"])
async def get_tempo_medio_aprovacao_prontuarios(
    start_date: datetime = Query(..., description="Data de início (YYYY-MM-DDTHH:MM:SS)"),
    end_date: datetime = Query(..., description="Data de fim (YYYY-MM-DDTHH:MM:SS)"),
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_view_reports)
):
    tenant_id = current_user.default_tenant_id
    return await crud.get_tempo_medio_aprovacao_prontuarios(db, tenant_id, start_date, end_date)

@router.get("/relatorios/visao-geral-agendamentos", response_model=schemas.VisaoGeralAgendamentos, tags=["Relatórios"])
async def get_visao_geral_agendamentos(
    start_date: datetime = Query(..., description="Data de início (YYYY-MM-DDTHH:MM:SS)"),
    end_date: datetime = Query(..., description="Data de fim (YYYY-MM-DDTHH:MM:SS)"),
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_view_reports)
):
    tenant_id = current_user.default_tenant_id
    return await crud.get_visao_geral_agendamentos(db, tenant_id, start_date, end_date)

@router.get("/relatorios/tratamentos-por-status", response_model=schemas.RelatorioTratamentosPorStatus, tags=["Relatórios"])
async def get_tratamentos_por_status(
    start_date: datetime = Query(..., description="Data de início (YYYY-MM-DDTHH:MM:SS)"),
    end_date: datetime = Query(..., description="Data de fim (YYYY-MM-DDTHH:MM:SS)"),
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_view_reports)
):
    tenant_id = current_user.default_tenant_id
    return await crud.get_tratamentos_por_status(db, tenant_id, start_date, end_date)

@router.get("/relatorios/resumo-financeiro", response_model=schemas.ResumoFinanceiro, tags=["Relatórios"])
async def get_resumo_financeiro(
    start_date: datetime = Query(..., description="Data de início (YYYY-MM-DDTHH:MM:SS)"),
    end_date: datetime = Query(..., description="Data de fim (YYYY-MM-DDTHH:MM:SS)"),
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_view_reports)
):
    tenant_id = current_user.default_tenant_id
    return await crud.get_resumo_financeiro(db, tenant_id, start_date, end_date)

@router.get("/relatorios/custos-tratamento-por-periodo", response_model=schemas.RelatorioCustosTratamento, tags=["Relatórios"])
async def get_custos_tratamento_por_periodo(
    start_date: datetime = Query(..., description="Data de início (YYYY-MM-DDTHH:MM:SS)"),
    end_date: datetime = Query(..., description="Data de fim (YYYY-MM-DDTHH:MM:SS)"),
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_view_reports)
):
    tenant_id = current_user.default_tenant_id
    return await crud.get_custos_tratamento_por_periodo(db, tenant_id, start_date, end_date)
