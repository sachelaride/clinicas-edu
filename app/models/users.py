import uuid
import enum
from sqlalchemy import Column, String, TIMESTAMP, Boolean, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ENUM
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db.base_class import Base
from .roles import UserRole # Import UserRole from new roles.py

# Association table for academic-advisor links
academic_advisor_link = Table(
    'academic_advisor_links', Base.metadata,
    Column('academic_id', PG_UUID(as_uuid=True), ForeignKey('system_users.id'), primary_key=True),
    Column('advisor_id', PG_UUID(as_uuid=True), ForeignKey('system_users.id'), primary_key=True)
)

class SystemUser(Base):
    __tablename__ = "system_users"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(255), unique=True, nullable=False, index=True) # New column
    senha_hash = Column(String, nullable=True)
    ldap_dn = Column(String, nullable=True)
    role = Column(ENUM(UserRole, name='user_role', create_type=False), nullable=False)
    especialidade = Column(String(255), nullable=True)
    ativo = Column(Boolean, default=True)
    default_tenant_id = Column(PG_UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    color = Column(String(7), nullable=True) # Stores hex color code, e.g., '#RRGGBB'
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships for academic-advisor links
    academics_linked_to_me = relationship(
        "SystemUser",
        secondary=academic_advisor_link,
        primaryjoin=id == academic_advisor_link.c.advisor_id,
        secondaryjoin=id == academic_advisor_link.c.academic_id,
        back_populates="my_advisors"
    )
    my_advisors = relationship(
        "SystemUser",
        secondary=academic_advisor_link,
        primaryjoin=id == academic_advisor_link.c.academic_id,
        secondaryjoin=id == academic_advisor_link.c.advisor_id,
        back_populates="academics_linked_to_me"
    )

    
