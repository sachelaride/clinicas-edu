from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid
from datetime import date, datetime, time, timedelta
from sqlalchemy.future import select

from ..crud import agendamentos as agendamentos_crud
from ..schemas import agendamentos as agendamentos_schemas
from ..db.database import get_db
from ..routes.auth import get_current_active_user
from ..models.users import SystemUser, UserRole
from ..core.permissions import can_create_appointment, can_read_appointment, can_update_appointment, can_delete_appointment
from ..models.feriados import Feriado
from ..models.agendamentos import Agendamento, AppointmentStatus

router = APIRouter()

@router.post("/", response_model=agendamentos_schemas.Agendamento, status_code=status.HTTP_201_CREATED, tags=["Agendamentos"])
async def create_agendamento(
    agendamento: agendamentos_schemas.AgendamentoCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: SystemUser = Depends(can_create_appointment)
):
    tenant_id = current_user.default_tenant_id
    return await agendamentos_crud.create_agendamento(db=db, agendamento=agendamento, tenant_id=tenant_id)

@router.get("/{agendamento_id}", response_model=agendamentos_schemas.Agendamento, tags=["Agendamentos"])
async def read_agendamento(
    agendamento_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user: SystemUser = Depends(can_read_appointment)
):
    tenant_id = current_user.default_tenant_id
    db_agendamento = await agendamentos_crud.get_agendamento(db, agendamento_id=agendamento_id, tenant_id=tenant_id)
    if db_agendamento is None:
        raise HTTPException(status_code=404, detail="Agendamento not found")
    return db_agendamento

@router.get("/", response_model=List[agendamentos_schemas.Agendamento], tags=["Agendamentos"])
async def read_agendamentos(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_read_appointment),
    academico_id: Optional[uuid.UUID] = None,
    orientador_id: Optional[uuid.UUID] = None,
    servico_id: Optional[uuid.UUID] = None,
    date: Optional[date] = None
):
    tenant_id = current_user.default_tenant_id # Get tenant_id from current_user
    if current_user.role == UserRole.admin_global:
        agendamentos = await agendamentos_crud.get_agendamentos(
            db,
            tenant_id=None,
            academico_id=academico_id,
            orientador_id=orientador_id,
            servico_id=servico_id,
            date=date,
            skip=skip,
            limit=limit
        )
    else:
        agendamentos = await agendamentos_crud.get_agendamentos(
            db,
            tenant_id=tenant_id,
            academico_id=academico_id,
            orientador_id=orientador_id,
            servico_id=servico_id,
            date=date,
            skip=skip,
            limit=limit
        )
    return agendamentos

@router.put("/{agendamento_id}", response_model=agendamentos_schemas.Agendamento, tags=["Agendamentos"])
async def update_agendamento(
    agendamento_id: uuid.UUID, 
    agendamento: agendamentos_schemas.AgendamentoUpdate, 
    db: AsyncSession = Depends(get_db), 
    current_user: SystemUser = Depends(can_update_appointment)
):
    tenant_id = current_user.default_tenant_id
    db_agendamento = await agendamentos_crud.update_agendamento(db, agendamento_id=agendamento_id, agendamento_data=agendamento, tenant_id=tenant_id)
    if db_agendamento is None:
        raise HTTPException(status_code=404, detail="Agendamento not found")
    return db_agendamento

@router.delete("/{agendamento_id}", response_model=agendamentos_schemas.Agendamento, tags=["Agendamentos"])
async def delete_agendamento(
    agendamento_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user: SystemUser = Depends(can_delete_appointment)
):
    tenant_id = current_user.default_tenant_id
    db_agendamento = await agendamentos_crud.delete_agendamento(db, agendamento_id=agendamento_id, tenant_id=tenant_id)
    if db_agendamento is None:
        raise HTTPException(status_code=404, detail="Agendamento not found")
    return db_agendamento

@router.get("/detalhes", response_model=List[agendamentos_schemas.AgendamentoDetalhes], tags=["Agendamentos"])
async def list_agendamentos_detalhes(
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_read_appointment),
    skip: int = 0,
    limit: int = 100
):
    tenant_id = current_user.default_tenant_id # Get tenant_id from current_user
    if current_user.role == UserRole.admin_global:
        agendamentos = await agendamentos_crud.get_agendamentos_detalhes(db, tenant_id=None, skip=skip, limit=limit)
    else:
        agendamentos = await agendamentos_crud.get_agendamentos_detalhes(db, tenant_id=tenant_id, skip=skip, limit=limit)
    return agendamentos

@router.get("/paciente/{paciente_id}", response_model=List[agendamentos_schemas.Agendamento], tags=["Agendamentos"])
async def read_agendamentos_by_paciente(
    paciente_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_read_appointment)
):
    tenant_id = current_user.default_tenant_id # Get tenant_id from current_user
    if current_user.role == UserRole.admin_global:
        agendamentos = await agendamentos_crud.get_agendamentos_by_paciente(
            db, paciente_id=paciente_id, tenant_id=None
        )
    else:
        agendamentos = await agendamentos_crud.get_agendamentos_by_paciente(
            db, paciente_id=paciente_id, tenant_id=tenant_id
        )
    return agendamentos

@router.post("/{agendamento_id}/iniciar", response_model=agendamentos_schemas.Agendamento, tags=["Agendamentos"])
async def iniciar_atendimento(
    agendamento_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_update_appointment)
):
    tenant_id = current_user.default_tenant_id
    db_agendamento = await agendamentos_crud.iniciar_atendimento(db, agendamento_id=agendamento_id, tenant_id=tenant_id)
    if db_agendamento is None:
        raise HTTPException(status_code=404, detail="Agendamento not found")
    return db_agendamento

@router.post("/{agendamento_id}/aguardar", response_model=agendamentos_schemas.Agendamento, tags=["Agendamentos"])
async def aguardar_atendimento(
    agendamento_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_update_appointment)
):
    tenant_id = current_user.default_tenant_id
    db_agendamento = await agendamentos_crud.aguardar_atendimento(db, agendamento_id=agendamento_id, tenant_id=tenant_id)
    if db_agendamento is None:
        raise HTTPException(status_code=404, detail="Agendamento not found")
    return db_agendamento

@router.post("/{agendamento_id}/em-atendimento", response_model=agendamentos_schemas.Agendamento, tags=["Agendamentos"])
async def em_atendimento(
    agendamento_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_update_appointment)
):
    tenant_id = current_user.default_tenant_id
    db_agendamento = await agendamentos_crud.em_atendimento(db, agendamento_id=agendamento_id, tenant_id=tenant_id)
    if db_agendamento is None:
        raise HTTPException(status_code=404, detail="Agendamento not found")
    return db_agendamento

@router.post("/{agendamento_id}/concluir", response_model=agendamentos_schemas.Agendamento, tags=["Agendamentos"])
async def concluir_atendimento(
    agendamento_id: uuid.UUID,
    observacoes: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_update_appointment)
):
    tenant_id = current_user.default_tenant_id
    db_agendamento = await agendamentos_crud.concluir_atendimento(
        db, 
        agendamento_id=agendamento_id, 
        tenant_id=tenant_id,
        observacoes=observacoes
    )
    if db_agendamento is None:
        raise HTTPException(status_code=404, detail="Agendamento not found")
    return db_agendamento

@router.get("/horarios-livres", response_model=List[time], tags=["Agendamentos"])
async def get_free_time_slots(
    target_date: date,
    duration_minutes: int,
    academico_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(get_current_active_user)
):
    # Input validation for duration_minutes
    if duration_minutes % 30 != 0 or not (30 <= duration_minutes <= 150):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A duração deve ser um múltiplo de 30 minutos e estar entre 30 e 150 minutos."
        )

    tenant_id = current_user.default_tenant_id # Get tenant_id from current_user

    # 1. Check for Sunday or Holiday
    if target_date.weekday() == 6:  # Sunday is 6
        return [] # No slots on Sunday

    # Check for holiday
    holiday_query = await db.execute(
        select(Feriado).where(
            Feriado.tenant_id == tenant_id,
            Feriado.data == target_date
        )
    )
    is_holiday = holiday_query.scalars().first() is not None

    if is_holiday:
        return [] # No slots on holidays

    # 2. Generate all possible 30-min slots
    start_time = datetime.combine(target_date, time(7, 0)) # 07:00
    end_time = datetime.combine(target_date, time(22, 0))   # 22:00

    all_possible_slots = []
    current_slot_start = start_time
    while current_slot_start < end_time:
        all_possible_slots.append(current_slot_start)
        current_slot_start += timedelta(minutes=30)

    # 3. Fetch booked appointments
    booked_slots_query = select(Agendamento).where(
        Agendamento.tenant_id == tenant_id,
        Agendamento.inicio >= datetime.combine(target_date, time(0, 0)),
        Agendamento.fim <= datetime.combine(target_date, time(23, 59, 59)),
        Agendamento.status.in_([
            AppointmentStatus.agendado,
            AppointmentStatus.iniciado,
            AppointmentStatus.aguardando,
            AppointmentStatus.em_atendimento
        ])
    )

    if academico_id:
        booked_slots_query = booked_slots_query.where(Agendamento.academico_id == academico_id)

    booked_appointments_result = await db.execute(booked_slots_query)
    booked_appointments = booked_appointments_result.scalars().all()

    # Create a set of all booked 30-minute intervals
    booked_intervals = set()
    for appt in booked_appointments:
        current_interval_start = datetime.combine(target_date, appt.inicio.time())
        while current_interval_start < datetime.combine(target_date, appt.fim.time()):
            booked_intervals.add(current_interval_start)
            current_interval_start += timedelta(minutes=30)

    free_slots_found = []
    slot_duration_td = timedelta(minutes=duration_minutes)
    num_30_min_blocks = duration_minutes // 30

    for possible_slot_start in all_possible_slots:
        # Check if this possible_slot_start is already booked
        if possible_slot_start in booked_intervals:
            continue

        # Check if the entire requested duration is free
        is_free_block = True
        for i in range(num_30_min_blocks):
            check_time = possible_slot_start + timedelta(minutes=i * 30)
            if check_time >= end_time or check_time in booked_intervals:
                is_free_block = False
                break
        
        if is_free_block:
            # Ensure the end of the proposed slot does not exceed working hours
            proposed_slot_end = possible_slot_start + slot_duration_td
            if proposed_slot_end <= end_time:
                free_slots_found.append(possible_slot_start.time())

    return free_slots_found
