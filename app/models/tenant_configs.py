
import uuid
import enum
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ENUM
from sqlalchemy.sql import func
from ..db.base_class import Base

class ConfigType(enum.Enum):
    email = "email"
    sms = "sms"

class ConfigKey(enum.Enum):
    smtp_host = "smtp_host"
    smtp_port = "smtp_port"
    smtp_user = "smtp_user"
    smtp_password = "smtp_password"
    smtp_use_ssl = "smtp_use_ssl"
    smtp_use_tls = "smtp_use_tls"
    sms_api_key = "sms_api_key"
    sms_sender_id = "sms_sender_id"

class TenantConfig(Base):
    __tablename__ = "tenant_configs"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PG_UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    config_type = Column(ENUM(ConfigType, name='config_type', create_type=False), nullable=False)
    config_key = Column(ENUM(ConfigKey, name='config_key', create_type=False), nullable=False)
    config_value = Column(Text, nullable=False)
    is_sensitive = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
