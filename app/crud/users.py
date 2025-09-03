import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models import users as models
from ..schemas import users as schemas
from ..core.security import get_password_hash
from fastapi import HTTPException, status
from typing import List
from sqlalchemy.orm import relationship
from ..models.roles import UserRole # Import UserRole from new roles.py

async def get_user(db: AsyncSession, user_id: uuid.UUID):
    result = await db.execute(
        select(models.SystemUser)
        .filter(models.SystemUser.id == user_id)
    )
    return result.scalars().first()

from sqlalchemy.orm import selectinload

async def get_user_by_username(db: AsyncSession, username: str):
    stmt = select(models.SystemUser).filter(models.SystemUser.username == username).options(selectinload(models.SystemUser.my_advisors))
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str):
    stmt = select(models.SystemUser).filter(models.SystemUser.email == email)
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100, tenant_id: uuid.UUID = None):
    stmt = select(models.SystemUser).options(selectinload(models.SystemUser.my_advisors))
    if tenant_id:
        stmt = stmt.filter(models.SystemUser.default_tenant_id == tenant_id)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().unique().all()

async def create_user(db: AsyncSession, user: schemas.UserCreate, ldap_dn: str = None):
    hashed_password = get_password_hash(user.password) if user.password else None
    
    # Ensure default_tenant_id is provided for new users
    if not user.default_tenant_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Default tenant ID is required for user creation.")

    user_data = user.model_dump(exclude={'academic_advisors', 'password', 'color'})
    db_user = models.SystemUser(**user_data, senha_hash=hashed_password, ldap_dn=ldap_dn, color=user.color)

    if user.academic_advisors and user.role == UserRole.academico:
        advisors_result = await db.execute(select(models.SystemUser).filter(models.SystemUser.id.in_(user.academic_advisors)))
        advisors = advisors_result.scalars().all()
        if len(advisors) != len(user.academic_advisors):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more academic advisors not found."
            )
        db_user.my_advisors = advisors
    elif user.role == UserRole.academico and not user.academic_advisors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Academic users must have at least one advisor."
        )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    # Ensure my_advisors relationship is loaded before returning
    await db.refresh(db_user, attribute_names=["my_advisors"])

    return db_user

async def update_user(db: AsyncSession, user_id: uuid.UUID, user_data: schemas.UserUpdate):
    result = await db.execute(select(models.SystemUser).filter(models.SystemUser.id == user_id))
    db_user = result.scalars().first()
    if db_user:
        update_data = user_data.model_dump(exclude_unset=True)
        
        if "academic_advisors" in update_data:
            if db_user.role == UserRole.academico:
                if not update_data["academic_advisors"]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Academic users must have at least one advisor."
                    )
                advisors_result = await db.execute(select(models.SystemUser).filter(models.SystemUser.id.in_(update_data["academic_advisors"])))
                advisors = advisors_result.scalars().all()
                if len(advisors) != len(update_data["academic_advisors"]):
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="One or more academic advisors not found."
                    )
                db_user.my_advisors = advisors
            del update_data["academic_advisors"]

        if "password" in update_data:
            if update_data["password"]:
                hashed_password = get_password_hash(update_data["password"])
                update_data["senha_hash"] = hashed_password
            del update_data["password"]
        
        for key, value in update_data.items():
            setattr(db_user, key, value)
        
        await db.commit()
        await db.refresh(db_user)
        # Ensure my_advisors relationship is loaded before returning
        await db.refresh(db_user, attribute_names=["my_advisors"])
    return db_user

async def delete_user(db: AsyncSession, user_id: uuid.UUID):
    result = await db.execute(select(models.SystemUser).filter(models.SystemUser.id == user_id))
    db_user = result.scalars().first()
    if db_user:
        await db.delete(db_user)
        await db.commit()
    return db_user

async def get_users_by_role(db: AsyncSession, role: UserRole, tenant_id: uuid.UUID):
    print(f"Fetching users for tenant_id: {tenant_id} and role: {role}")
    
    stmt = select(models.SystemUser)
    stmt = stmt.filter(models.SystemUser.default_tenant_id == tenant_id, models.SystemUser.role == role.value)

    print(f"SQL Statement: {stmt}")
    result = await db.execute(stmt)
    return result.scalars().all()
