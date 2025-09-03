from pydantic import BaseModel, UUID4
import datetime

class TenantBase(BaseModel):
    nome: str
    cnpj: str

class TenantCreate(TenantBase):
    pass

class TenantUpdate(BaseModel):
    nome: str | None = None
    cnpj: str | None = None

class Tenant(TenantBase):
    id: UUID4
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True
