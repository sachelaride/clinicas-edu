from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..crud import menu_permissions as menu_permissions_crud
from ..schemas import menu_permissions as menu_permissions_schemas
from ..db.database import get_db
from .auth import get_current_active_user
from ..models.users import SystemUser
from ..models.roles import UserRole
from ..models.menu_permissions import MenuKey
from ..core.permissions import can_manage_menu_permissions

router = APIRouter()

@router.get("/permissions/{role}", response_model=List[menu_permissions_schemas.MenuPermission], tags=["Permissions"])
async def get_permissions(
    role: UserRole,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_manage_menu_permissions)
):
    return await menu_permissions_crud.get_menu_permissions_by_role(db, role=role)

@router.put("/permissions/{role}/{menu_key}", response_model=menu_permissions_schemas.MenuPermission, tags=["Permissions"])
async def update_permission(
    role: UserRole,
    menu_key: MenuKey,
    permission_update: menu_permissions_schemas.MenuPermissionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_manage_menu_permissions)
):
    return await menu_permissions_crud.update_menu_permission(db, role=role, menu_key=menu_key, can_access=permission_update.can_access)

@router.post("/permissions/init", tags=["Permissions"])
async def init_permissions(
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(can_manage_menu_permissions)
):
    await menu_permissions_crud.create_initial_permissions(db)
    return {"message": "Initial permissions created successfully."}
