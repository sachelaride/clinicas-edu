from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Importa o objeto de configurações centralizadas.
from ..core.config import settings

# Cria o motor (engine) de conexão assíncrona com o banco de dados.
# A URL de conexão é lida diretamente do nosso objeto de configurações.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Mude para True para ver os comandos SQL gerados no console
)

# Cria uma fábrica de sessões assíncronas.
# expire_on_commit=False é importante para que os objetos não expirem após o commit,
# o que é útil em APIs FastAPI.
AsyncSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession, expire_on_commit=False
)

# Cria uma classe base para os modelos declarativos do SQLAlchemy.
Base = declarative_base()

# Dependência para obter uma sessão de banco de dados em cada requisição.
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
