from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
import os
import uuid # Import uuid
from typing import Optional # Import Optional
from ..core.config import settings # Import settings

from ..crud import users as users_crud
from ..schemas import token as token_schema
from ..schemas import users as user_schema
from ..core import security
from ..db.database import get_db
from ..models.users import SystemUser, UserRole
from ..core.ldap import authenticate_ldap_user

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

@router.post("/token", response_model=token_schema.Token, tags=["Authentication"])
async def login_for_access_token(db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    print(f"DEBUG: form_data.username: {form_data.username}")
    print(f"DEBUG: form_data.password: {form_data.password}")
    # Try LDAP authentication first
    ldap_user_info = authenticate_ldap_user(form_data.username, form_data.password)
    
    if ldap_user_info:
        # LDAP authentication successful
        user = await users_crud.get_user_by_username(db, username=form_data.username) # Use get_user_by_username
        if not user:
            # User exists in LDAP but not in the local DB, create it
            user_to_create = user_schema.UserCreate(
                username=form_data.username, # Use username
                email=ldap_user_info['mail'], # Assuming LDAP provides 'mail' attribute for email
                nome=ldap_user_info['cn'],
                role=UserRole.academico, # Default role
                password=os.urandom(16).hex() # Generate a random password
            )
            user = await users_crud.create_user(db, user_to_create, ldap_dn=ldap_user_info['dn'])
    else:
        # Fallback to local authentication
        user = await users_crud.get_user_by_username(db, username=form_data.username) # Use get_user_by_username
        print(f"DEBUG: User retrieved from DB: {user}")
        if not user or not security.verify_password(form_data.password, user.senha_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # default_tenant_id is now non-nullable, so it must be set during user creation.
    # No need for user_tenants_crud logic here.
    if not user.default_tenant_id:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User does not have a default tenant assigned.")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username, "tenant_id": str(user.default_tenant_id)}, expires_delta=access_token_expires # Include tenant_id in token
    )
    return {"access_token": access_token, "token_type": "bearer", "default_tenant_id": user.default_tenant_id}

async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)) -> SystemUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    print(f"DEBUG: Token received in get_current_user: {token}")
    token_data = security.decode_access_token(token)
    print(f"DEBUG: Decoded token data: {token_data}")
    if token_data is None or token_data.username is None: # Use token_data.username
        raise credentials_exception
    user = await users_crud.get_user_by_username(db, username=token_data.username) # Use get_user_by_username and token_data.username
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: user_schema.User = Depends(get_current_user)
) -> user_schema.User:
    if not current_user.ativo:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user