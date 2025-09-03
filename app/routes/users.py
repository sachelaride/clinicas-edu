from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from ..crud import users as users_crud
from ..schemas import users as users_schemas
from ..db.database import get_db
from .auth import get_current_active_user
from ..models.users import SystemUser
from ..models.roles import UserRole
from ..core.permissions import can_create_users, can_read_users, can_manage_users

router = APIRouter()

@router.get("/me", response_model=users_schemas.User, tags=["Users"])
async def read_users_me(current_user: users_schemas.User = Depends(get_current_active_user)):
    return current_user

@router.post("/", response_model=users_schemas.User, status_code=201, tags=["Users"])
async def create_user(
    user: users_schemas.UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(get_current_active_user) # Inject current user
):
    """
    Cria um novo usuário no sistema, com validação de permissões baseada no papel do usuário logado.
    """
    # Check if email already registered
    db_user = await users_crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Permission logic
    if current_user.role == UserRole.admin_global:
        # Admin global can create any user role
        pass
    elif current_user.role == UserRole.gestor_clinica:
        # Gestor de Clínica can create academico or gestor_clinica
        if user.role not in [UserRole.academico, UserRole.gestor_clinica]:
            raise HTTPException(
                status_code=403,
                detail=f"Gestor de Clínica cannot create user with role {user.role.value}"
            )
    elif current_user.role == UserRole.recepcao or current_user.role == UserRole.orientador:
        # Recepcionista and Orientador can only create academico
        if user.role != UserRole.academico:
            raise HTTPException(
                status_code=403,
                detail=f"{current_user.role.value} cannot create user with role {user.role.value}"
            )
    else:
        # Other roles (e.g., academico) cannot create users
        raise HTTPException(
            status_code=403,
            detail=f"User with role {current_user.role.value} is not authorized to create users."
        )

    return await users_crud.create_user(db=db, user=user)

@router.get("/", response_model=List[users_schemas.User], tags=["Users"])
async def read_users(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: SystemUser = Depends(get_current_active_user)
):
    if current_user.role == UserRole.admin_global:
        users = await users_crud.get_users(db, skip=skip, limit=limit) # Get all users
    else:
        # Pass the tenant_id from the logged-in user to the CRUD function
        users = await users_crud.get_users(db, skip=skip, limit=limit, tenant_id=current_user.default_tenant_id)
    return users

@router.get("/{user_id}", response_model=users_schemas.User, tags=["Users"])
async def read_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Obtém os detalhes de um usuário específico pelo seu ID.
    """
    db_user = await users_crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=users_schemas.User, tags=["Users"])
async def update_user(user_id: uuid.UUID, user: users_schemas.UserUpdate, db: AsyncSession = Depends(get_db)):
    """
    Atualiza as informações de um usuário.
    """
    db_user = await users_crud.update_user(db, user_id=user_id, user_data=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.delete("/{user_id}", response_model=users_schemas.User, tags=["Users"])
async def delete_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Remove um usuário do sistema.
    """
    db_user = await users_crud.delete_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get("/role/{role_name}", response_model=List[users_schemas.UserRoleResponse], tags=["Users"])
async def read_users_by_role(
    role_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: SystemUser = Depends(get_current_active_user)
):
    try:
        role = UserRole[role_name]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Role '{role_name}' not found.")
    
    tenant_id = current_user.default_tenant_id # Get tenant_id from current_user
    users = await users_crud.get_users_by_role(db, role=role, tenant_id=tenant_id)
    return users