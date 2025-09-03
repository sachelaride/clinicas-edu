import enum

class UserRole(enum.Enum):
    admin_global = "admin_global"
    gestor_clinica = "gestor_clinica"
    recepcao = "recepcao"
    academico = "academico"
    orientador = "orientador"
