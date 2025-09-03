from pydantic import BaseModel, UUID4
import datetime
from typing import Optional

class FeriadoBase(BaseModel):
    data: datetime.date
    nome: str

class FeriadoCreate(FeriadoBase):
    pass

class FeriadoUpdate(BaseModel):
    data: Optional[datetime.date] = None
    nome: Optional[str] = None

class Feriado(FeriadoBase):
    id: UUID4
    tenant_id: UUID4
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True
