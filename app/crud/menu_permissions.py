from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import cast, Text
from ..models import menu_permissions as models
from ..schemas import menu_permissions as schemas
from ..models.roles import UserRole # Import UserRole from new roles.py

async def get_menu_permissions_by_role(db: AsyncSession, role: UserRole):
    stmt = select(models.MenuPermission).filter(cast(models.MenuPermission.role, Text) == role.value)
    result = await db.execute(stmt)
    return result.scalars().all()

async def update_menu_permission(db: AsyncSession, role: UserRole, menu_key: str, permission_data: schemas.MenuPermissionUpdate):
    stmt = select(models.MenuPermission).filter(cast(models.MenuPermission.role, Text) == role.value, cast(models.MenuPermission.menu_key, Text) == menu_key)
    result = await db.execute(stmt)
    permission = result.scalars().first()
    if permission:
        update_data = permission_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(permission, key, value)
        try:
            await db.commit()
            await db.refresh(permission)
        except Exception as e:
            await db.rollback()
            raise e
    return permission

async def create_initial_permissions(db: AsyncSession):
    # Create default permissions for all roles and menus
    permissions_to_add = []
    for role in UserRole:
        for menu_key in models.MenuKey:
            # Check if permission already exists
            stmt = select(models.MenuPermission).filter(cast(models.MenuPermission.role, Text) == role.value, cast(models.MenuPermission.menu_key, Text) == menu_key.value)
            result = await db.execute(stmt)
            permission = result.scalars().first()
            if not permission:
                can_access = False

                if role == UserRole.admin_global:
                    can_access = True
                elif role == UserRole.gestor_clinica:
                    if menu_key in [models.MenuKey.TENANTS, models.MenuKey.USERS, models.MenuKey.PATIENTS, models.MenuKey.SERVICES, models.MenuKey.APPOINTMENTS, models.MenuKey.PRONTUARIOS, models.MenuKey.TRATAMENTOS, models.MenuKey.PLANOS_CUSTO, models.MenuKey.ESTOQUE, models.MenuKey.CONSENTIMENTOS, models.MenuKey.RELATORIOS_ACADEMICOS, models.MenuKey.DASHBOARDS_GERENCIAIS]:
                        can_access = True
                elif role == UserRole.recepcao:
                    if menu_key in [models.MenuKey.PATIENTS, models.MenuKey.APPOINTMENTS, models.MenuKey.CONSENTIMENTOS]:
                        can_access = True
                elif role == UserRole.academico:
                    if menu_key in [models.MenuKey.PATIENTS, models.MenuKey.APPOINTMENTS, models.MenuKey.PRONTUARIOS, models.MenuKey.TRATAMENTOS, models.MenuKey.CONSENTIMENTOS]:
                        can_access = True
                elif role == UserRole.orientador:
                    if menu_key in [models.MenuKey.PATIENTS, models.MenuKey.PRONTUARIOS, models.MenuKey.TRATAMENTOS, models.MenuKey.RELATORIOS_ACADEMICOS]:
                        can_access = True

                permissions_to_add.append(models.MenuPermission(
                    role=role,
                    menu_key=menu_key,
                    can_access=can_access
                ))
    if permissions_to_add:
        db.add_all(permissions_to_add)
        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise e
