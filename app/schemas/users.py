from pydantic import BaseModel, UUID4, EmailStr
import datetime
from typing import Optional, List, Dict # Import Dict
from ..models.roles import UserRole # Import UserRole from new roles.py

class UserTenantAssociation(BaseModel): # New schema
    tenant_id: UUID4
    role: UserRole

class UserBase(BaseModel):
    username: str # New field
    email: EmailStr
    nome: str
    role: UserRole
    especialidade: Optional[str] = None
    ativo: bool = True
    default_tenant_id: Optional[UUID4] = None
    color: Optional[str] = None

class UserCreate(UserBase):
    password: Optional[str] = None
    user_tenants: Optional[List[UserTenantAssociation]] = None
    academic_advisors: Optional[List[UUID4]] = None # New field

class UserUpdate(BaseModel):
    username: Optional[str] = None # New field
    email: Optional[EmailStr] = None
    nome: Optional[str] = None
    role: Optional[UserRole] = None
    especialidade: Optional[str] = None
    ativo: Optional[bool] = None
    default_tenant_id: Optional[UUID4] = None
    color: Optional[str] = None
    password: Optional[str] = None
    user_tenants: Optional[List[UserTenantAssociation]] = None
    academic_advisors: Optional[List[UUID4]] = None # New field

class User(UserBase):
    id: UUID4
    especialidade: Optional[str] = None
    ativo: Optional[bool] = None
    default_tenant_id: Optional[UUID4] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    my_advisors: Optional[List['UserSimple']] = []
    user_tenants: Optional[List[UserTenantAssociation]] = [] # Add user_tenants to User schema

    class Config:
        from_attributes = True

class UserSimple(BaseModel):
    id: UUID4
    nome: str
    email: EmailStr
    username: str
    role: UserRole
    color: Optional[str] = None

    class Config:
        from_attributes = True

class UserRoleResponse(BaseModel):
    id: UUID4
    nome: str
    username: str
    role: UserRole

    class Config:
        from_attributes = True

# Forward reference for recursive type
User.model_rebuild()
