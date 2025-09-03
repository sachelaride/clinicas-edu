from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    """
    Classe para gerenciar as configurações da aplicação.
    O Pydantic-Settings carrega automaticamente as variáveis de um arquivo .env
    ou das variáveis de ambiente do sistema.
    """
    
    # Configurações do Banco de Dados
    # Exemplo: postgresql+asyncpg://user:password@host/dbname
    DATABASE_URL: str

    # Configurações de Segurança JWT
    # Para gerar uma chave segura, você pode usar o comando:
    # openssl rand -hex 32
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Directory for file uploads (documents, prontuarios)
    BASE_UPLOAD_DIR: str = "data/uploads"

    # Carrega as configurações de um arquivo .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

    # Theme settings
    DEFAULT_THEME: str = "light"

# Instancia única das configurações que será usada em toda a aplicação.
settings = Settings()
