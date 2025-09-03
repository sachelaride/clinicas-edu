from contextvars import ContextVar
from sqlalchemy.ext.asyncio import AsyncSession

# Context variable to store the current tenant ID for each request
current_tenant_id: ContextVar[str | None] = ContextVar("current_tenant_id", default=None)

# You might also want a session factory here if you are not using the one in database.py
