# Importações de bibliotecas e módulos necessários.
# FastAPI: O framework principal para a construção da API.
# Request: Usado para obter detalhes das requisições HTTP recebidas.
# JSONResponse: Usado para criar respostas HTTP com corpo em formato JSON customizado.
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Import CORSMiddleware

# Importa exceções específicas do SQLAlchemy para tratamento de erros de banco de dados.
from sqlalchemy.exc import IntegrityError

# Importa todos os módulos de rotas da aplicação. Cada módulo define um conjunto de endpoints relacionados.
from .routes import (
    auth, users, tenants, pacientes, responsaveis, servicos, 
    agendamentos, prontuarios, tratamentos, tratamento_servicos, planos_custo, 
    estoque, consentimentos_paciente, tenant_configs, relatorios, menu_permissions,
    documentos_paciente, pagamentos, despesas
)

app = FastAPI()

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # URL do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(tenants.router, prefix="/tenants", tags=["Tenants"])
app.include_router(pacientes.router, prefix="/pacientes", tags=["Pacientes"])
app.include_router(responsaveis.router, prefix="/responsaveis", tags=["Responsaveis"])
app.include_router(servicos.router, prefix="/servicos", tags=["Servicos"])
app.include_router(agendamentos.router, prefix="/agendamentos", tags=["Agendamentos"])
app.include_router(prontuarios.router, prefix="/prontuarios", tags=["Prontuarios"])
app.include_router(tratamentos.router, prefix="/tratamentos", tags=["Tratamentos"])
app.include_router(tratamento_servicos.router, prefix="/tratamento-servicos", tags=["Tratamentos Servicos"])
app.include_router(planos_custo.router, prefix="/planos-custo", tags=["Planos de Custo"])
app.include_router(estoque.router, prefix="/estoque", tags=["Estoque"])
app.include_router(consentimentos_paciente.router, prefix="/consentimentos-paciente", tags=["Consentimentos"])
app.include_router(tenant_configs.router, prefix="/tenant-configs", tags=["Tenant Configs"])
app.include_router(relatorios.router, prefix="/relatorios", tags=["Relatórios"])
app.include_router(menu_permissions.router, prefix="/menu-permissions", tags=["Menu Permissions"])
app.include_router(documentos_paciente.router, prefix="/documentos-paciente", tags=["Documentos Paciente"])
app.include_router(pagamentos.router, prefix="/pagamentos", tags=["Pagamentos"])
app.include_router(despesas.router, prefix="/despesas", tags=["Despesas"])

@app.get("/")
def read_root():
    return {"message": "API is running"}