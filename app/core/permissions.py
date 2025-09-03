from fastapi import Depends, HTTPException, status
from ..models.users import SystemUser, UserRole
from ..routes.auth import get_current_active_user

def has_permission(allowed_roles: list[UserRole]):
    def _has_permission(current_user: SystemUser = Depends(get_current_active_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have enough permissions to perform this action."
            )
        return current_user
    return _has_permission

# Permissions for patient management
can_create_patient = has_permission([UserRole.admin_global, UserRole.gestor_clinica, UserRole.recepcao])
can_read_patient = has_permission([UserRole.admin_global, UserRole.gestor_clinica, UserRole.recepcao, UserRole.academico, UserRole.orientador])
can_update_patient = has_permission([UserRole.admin_global, UserRole.gestor_clinica, UserRole.recepcao])
can_delete_patient = has_permission([UserRole.admin_global, UserRole.gestor_clinica])

# Permissions for appointment management
can_create_appointment = has_permission([UserRole.admin_global, UserRole.gestor_clinica, UserRole.recepcao, UserRole.academico, UserRole.orientador])
can_read_appointment = has_permission([UserRole.admin_global, UserRole.gestor_clinica, UserRole.recepcao, UserRole.academico, UserRole.orientador])
can_update_appointment = has_permission([UserRole.admin_global, UserRole.gestor_clinica, UserRole.recepcao, UserRole.academico, UserRole.orientador])
can_delete_appointment = has_permission([UserRole.admin_global, UserRole.gestor_clinica])

# Permissions for services (procedimentos)
can_manage_services = has_permission([UserRole.admin_global, UserRole.gestor_clinica])
can_create_update_services = has_permission([UserRole.admin_global, UserRole.gestor_clinica, UserRole.recepcao, UserRole.academico, UserRole.orientador])
can_read_services = has_permission([UserRole.admin_global, UserRole.gestor_clinica, UserRole.recepcao, UserRole.academico, UserRole.orientador])

# Permissions for medical records (prontuarios)
can_manage_records = has_permission([UserRole.admin_global, UserRole.gestor_clinica])
can_create_update_records = has_permission([UserRole.admin_global, UserRole.gestor_clinica, UserRole.recepcao, UserRole.academico, UserRole.orientador])
can_read_records = has_permission([UserRole.admin_global, UserRole.gestor_clinica, UserRole.recepcao, UserRole.academico, UserRole.orientador])

# Permissions for stock management (estoque)
can_manage_stock = has_permission([UserRole.admin_global, UserRole.gestor_clinica])
can_create_update_stock = has_permission([UserRole.admin_global, UserRole.gestor_clinica, UserRole.recepcao, UserRole.academico, UserRole.orientador])
can_read_stock = has_permission([UserRole.admin_global, UserRole.gestor_clinica, UserRole.recepcao, UserRole.academico, UserRole.orientador])

# Permissions for cost plans (planos de custo)
can_manage_cost_plans = has_permission([UserRole.admin_global, UserRole.gestor_clinica])
can_create_update_cost_plans = has_permission([UserRole.admin_global, UserRole.gestor_clinica, UserRole.recepcao, UserRole.orientador])
can_read_cost_plans = has_permission([UserRole.admin_global, UserRole.gestor_clinica, UserRole.recepcao, UserRole.orientador])

# Permissions for payments (pagamentos)
can_manage_payments = has_permission([UserRole.admin_global, UserRole.gestor_clinica, UserRole.recepcao])

# Permissions for consents (consentimentos)
can_manage_consent = has_permission([UserRole.admin_global, UserRole.gestor_clinica, UserRole.recepcao])

# Permissions for reports (relatorios)
can_view_reports = has_permission([UserRole.admin_global, UserRole.gestor_clinica, UserRole.orientador])

# Permissions for tenants (clinicas)
can_manage_tenants = has_permission([UserRole.admin_global])

# Permissions for users (usuarios)
can_manage_users = has_permission([UserRole.admin_global, UserRole.gestor_clinica])
can_create_users = has_permission([UserRole.admin_global, UserRole.gestor_clinica, UserRole.recepcao])
can_read_users = has_permission([UserRole.admin_global, UserRole.gestor_clinica])

# Permissions for menu permissions
can_manage_menu_permissions = has_permission([UserRole.admin_global])

# Permissions for treatments (tratamentos)
can_create_treatment = has_permission([UserRole.admin_global, UserRole.gestor_clinica, UserRole.recepcao, UserRole.academico, UserRole.orientador])
can_read_treatment = has_permission([UserRole.admin_global, UserRole.gestor_clinica, UserRole.recepcao, UserRole.academico, UserRole.orientador])
can_update_treatment = has_permission([UserRole.admin_global, UserRole.gestor_clinica, UserRole.recepcao, UserRole.academico, UserRole.orientador])
can_delete_treatment = has_permission([UserRole.admin_global, UserRole.gestor_clinica])
can_finalize_treatment = has_permission([UserRole.admin_global, UserRole.gestor_clinica, UserRole.academico, UserRole.orientador])
can_activate_treatment = has_permission([UserRole.admin_global, UserRole.gestor_clinica, UserRole.recepcao, UserRole.academico, UserRole.orientador])
