
from pydantic import BaseModel, UUID4
import datetime
from typing import Optional
from ..models.tenant_configs import ConfigType, ConfigKey

class TenantConfigBase(BaseModel):
    config_type: ConfigType
    config_key: ConfigKey
    config_value: str
    is_sensitive: Optional[bool] = False

class TenantConfigCreate(TenantConfigBase):
    pass

class TenantConfigUpdate(BaseModel):
    config_value: Optional[str] = None
    is_sensitive: Optional[bool] = None

class TenantConfig(TenantConfigBase):
    id: UUID4
    tenant_id: UUID4
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True
