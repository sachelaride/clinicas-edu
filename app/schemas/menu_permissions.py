from pydantic import BaseModel, UUID4
from ..models.roles import UserRole # Import UserRole from new roles.py
from ..models.menu_permissions import MenuKey
from typing import Optional

class MenuPermissionBase(BaseModel):
    role: UserRole
    menu_key: MenuKey
    can_access: bool

class MenuPermissionCreate(MenuPermissionBase):
    pass

class MenuPermissionUpdate(BaseModel):
    role: Optional[UserRole] = None
    menu_key: Optional[MenuKey] = None
    can_access: Optional[bool] = None

class MenuPermission(MenuPermissionBase):
    id: UUID4

    class Config:
        from_attributes = True