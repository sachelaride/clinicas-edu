# 🚀 Guia de Instalação e Execução - Sistema de Clínicas Educacionais

## 📋 Pré-requisitos

### Sistema Operacional
- **Linux**: Ubuntu 20.04+ (recomendado)
- **Windows**: Windows 10+ com WSL2
- **macOS**: macOS 10.15+

### Python
- **Versão**: Python 3.8 ou superior
- **Recomendado**: Python 3.11

### Banco de Dados
- **PostgreSQL**: 12+ (para produção)
- **SQLite**: Para desenvolvimento local

## 🔧 Instalação

### 1. Clone o Repositório
```bash
git clone https://github.com/sachelaride/clinicas-edu.git
cd clinicas-edu
```

### 2. Crie um Ambiente Virtual
```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 3. Instale as Dependências
```bash
# Dependências principais
pip install kivy fastapi uvicorn sqlalchemy asyncpg httpx

# Dependências adicionais
pip install pydantic-settings "pydantic[email]"

# Para desenvolvimento (opcional)
pip install pytest black flake8
```

### 4. Configuração do Banco de Dados

#### Para Desenvolvimento (SQLite):
```bash
# O sistema criará automaticamente o banco SQLite
# Nenhuma configuração adicional necessária
```

#### Para Produção (PostgreSQL):
```bash
# Instale o PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Crie o banco de dados
sudo -u postgres createdb clinicas_edu

# Configure as variáveis de ambiente
export DATABASE_URL="postgresql://usuario:senha@localhost/clinicas_edu"
```

### 5. Configuração de Variáveis de Ambiente
```bash
# Crie um arquivo .env na raiz do projeto
cat > .env << EOF
DATABASE_URL=sqlite:///./clinicas_edu.db
SECRET_KEY=sua_chave_secreta_aqui
DEBUG=True
EOF
```

## ▶️ Execução

### 1. Executar o Backend (API)
```bash
# Em um terminal, navegue até o diretório do projeto
cd clinicas-edu

# Execute o servidor FastAPI
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

O backend estará disponível em: `http://localhost:8000`

### 2. Executar o Frontend (Kivy)

#### Versão Melhorada (Recomendada):
```bash
# Em outro terminal, no mesmo diretório
python main_improved.py
```

#### Versão Original:
```bash
python main.py
```

### 3. Verificar a Instalação
```bash
# Execute os testes do sistema
python test_system.py
```

## 🎨 Configuração de Temas

### Temas Disponíveis:
1. **Médico Moderno** (Padrão)
2. **Médico Escuro**
3. **Verde Suave**
4. **Padrão**
5. **Escuro**
6. **Médico**
7. **Moderno**

### Alterar Tema Padrão:
Edite o arquivo `main_improved.py`:
```python
# Linha 35, altere o tema padrão:
theme_manager.set_theme('dark_medical')  # ou outro tema
```

## 🔧 Configurações Avançadas

### 1. Configuração de CORS
Para permitir acesso de outros domínios, edite `app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://seudominio.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. Configuração de Logging
```python
import logging

# Configure o nível de log
logging.basicConfig(level=logging.INFO)
```

### 3. Configuração de Produção
```bash
# Use um servidor WSGI para produção
pip install gunicorn

# Execute com Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 🐛 Solução de Problemas

### Erro: "ModuleNotFoundError"
```bash
# Verifique se o ambiente virtual está ativo
source venv/bin/activate

# Reinstale as dependências
pip install -r requirements.txt
```

### Erro: "Permission denied"
```bash
# No Linux, pode ser necessário instalar dependências do sistema
sudo apt-get install python3-dev libpq-dev

# Para Kivy no Linux
sudo apt-get install python3-kivy
```

### Erro: "Database connection failed"
```bash
# Verifique se o PostgreSQL está rodando
sudo systemctl status postgresql

# Verifique as credenciais no arquivo .env
cat .env
```

### Erro: "Port already in use"
```bash
# Encontre o processo usando a porta
lsof -i :8000

# Mate o processo
kill -9 <PID>

# Ou use uma porta diferente
uvicorn app.main:app --port 8001
```

## 📊 Monitoramento

### 1. Logs da Aplicação
```bash
# Logs do FastAPI
tail -f logs/app.log

# Logs do Kivy
tail -f ~/.kivy/logs/kivy_*.txt
```

### 2. Métricas de Performance
```bash
# Instale ferramentas de monitoramento
pip install psutil

# Monitor de recursos
python -c "import psutil; print(f'CPU: {psutil.cpu_percent()}%, RAM: {psutil.virtual_memory().percent}%')"
```

## 🔄 Atualizações

### 1. Atualizar o Sistema
```bash
# Baixe as últimas alterações
git pull origin main

# Atualize as dependências
pip install -r requirements.txt --upgrade

# Execute as migrações (se houver)
python manage.py migrate
```

### 2. Backup dos Dados
```bash
# Backup do banco SQLite
cp clinicas_edu.db clinicas_edu_backup_$(date +%Y%m%d).db

# Backup do PostgreSQL
pg_dump clinicas_edu > backup_$(date +%Y%m%d).sql
```

## 🧪 Desenvolvimento

### 1. Executar Testes
```bash
# Testes do sistema
python test_system.py

# Testes unitários (se configurados)
pytest tests/

# Testes de cobertura
pytest --cov=app tests/
```

### 2. Formatação de Código
```bash
# Formatar código Python
black .

# Verificar estilo
flake8 .
```

### 3. Estrutura de Desenvolvimento
```
clinicas-edu/
├── app/                    # Backend FastAPI
│   ├── core/              # Configurações centrais
│   ├── models/            # Modelos de dados
│   ├── routes/            # Rotas da API
│   ├── schemas/           # Schemas Pydantic
│   └── services/          # Lógica de negócio
├── screens/               # Telas Kivy
├── themes/                # Arquivos de tema
├── tests/                 # Testes automatizados
└── docs/                  # Documentação
```

## 📚 Recursos Adicionais

### Documentação da API
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Documentação das Tecnologias
- **Kivy**: https://kivy.org/doc/stable/
- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/

### Comunidade e Suporte
- **Issues**: Reporte problemas no GitHub
- **Discussões**: Use as discussões do repositório
- **Wiki**: Consulte a wiki para tutoriais avançados

---

**Para suporte técnico, consulte a documentação ou abra uma issue no repositório.**

