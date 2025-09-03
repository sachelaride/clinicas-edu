import uuid
import enum
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ENUM
from ..db.base_class import Base
from .users import UserRole

class MenuKey(str, enum.Enum):
    TENANTS = "TENANTS"
    USERS = "USERS"
    PATIENTS = "PATIENTS"
    SERVICES = "SERVICES"
    APPOINTMENTS = "APPOINTMENTS"
    PRONTUARIOS = "PRONTUARIOS"
    TRATAMENTOS = "TRATAMENTOS"
    PLANOS_CUSTO = "PLANOS_CUSTO"
    ESTOQUE = "ESTOQUE"
    CONSENTIMENTOS = "CONSENTIMENTOS"
    RELATORIOS_ACADEMICOS = "RELATORIOS_ACADEMICOS"
    DASHBOARDS_GERENCIAIS = "DASHBOARDS_GERENCIAIS"

class MenuPermission(Base):
    __tablename__ = "menu_permissions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role = Column(ENUM(UserRole, name='user_role', create_type=False), nullable=False)
    menu_key = Column(ENUM(MenuKey, name='menu_key', create_type=False), nullable=False)
    can_access = Column(Boolean, default=False)