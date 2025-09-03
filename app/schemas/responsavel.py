from pydantic import BaseModel, Field
from typing import Optional
import uuid
from datetime import datetime

class ResponsavelBase(BaseModel):
    nome: str = Field(..., max_length=255)
    telefone: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=255)
    documento: Optional[str] = Field(None, max_length=255)

class ResponsavelCreate(ResponsavelBase):
    pass

class ResponsavelUpdate(ResponsavelBase):
    pass

class ResponsavelInDB(ResponsavelBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True