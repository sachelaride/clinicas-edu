from pydantic import BaseModel
import uuid
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str
    default_tenant_id: Optional[uuid.UUID] = None

class TokenData(BaseModel):
    username: str | None = None # Change email to username
