# Importações de bibliotecas para manipulação de data/hora, tipos e segurança.
from datetime import datetime, timedelta, timezone
from typing import Optional

# 'jose' (Javascript Object Signing and Encryption) é uma biblioteca para trabalhar com JWT (JSON Web Tokens).
from jose import JWTError, jwt

# 'passlib' é uma biblioteca para hashing de senhas. Ela abstrai os detalhes dos algoritmos de hash.
from passlib.context import CryptContext

# Importa o objeto de configurações centralizadas.
from .config import settings
# Importa o schema Pydantic para os dados contidos no token.
from ..schemas.token import TokenData

# --- Hashing de Senhas ---

# Cria um contexto de criptografia usando passlib.
# schemes=["bcrypt"]: Especifica que o bcrypt é o algoritmo de hash padrão e preferido.
# deprecated="auto": Permite que o passlib verifique senhas com algoritmos mais antigos, mas sempre usará o bcrypt para novos hashes.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Função para verificar se uma senha em texto plano corresponde a uma senha com hash.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compara uma senha de texto plano com seu hash armazenado no banco de dados.
    Retorna True se a senha for válida, False caso contrário.
    """
    return pwd_context.verify(plain_password, hashed_password)

# Função para gerar o hash de uma senha em texto plano.
def get_password_hash(password: str) -> str:
    """
    Calcula o hash de uma senha usando o algoritmo bcrypt.
    """
    return pwd_context.hash(password)

# --- Manipulação de Token JWT ---

# Função para criar um novo token de acesso JWT.
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Gera um token JWT assinado.
    :param data: Dicionário com os dados a serem incluídos no payload do token (o "claim").
    :param expires_delta: Tempo opcional para a expiração do token.
    """
    # Cria uma cópia dos dados para não modificar o dicionário original.
    to_encode = data.copy()
    
    # Calcula o tempo de expiração do token.
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Se nenhum tempo de expiração for fornecido, usa um padrão de 15 minutos.
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    # Adiciona o campo "exp" (expiration time) ao payload do token. Este é um campo padrão do JWT.
    to_encode.update({"exp": expire})
    
    # Codifica o payload em um token JWT, usando a chave secreta e o algoritmo das configurações.
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt

# Função para decodificar um token de acesso e validar seus dados.
def decode_access_token(token: str):
    """
    Verifica a assinatura e a validade de um token JWT e extrai o payload. 
    """
    try:
        # Tenta decodificar o token. A função `jwt.decode` automaticamente verifica a assinatura e a expiração.
        # Se o token for inválido ou expirado, uma exceção `JWTError` será lançada.
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Extrai o username do campo "sub" (subject), que é o identificador do usuário no nosso caso.
        username: str = payload.get("sub")
        
        # Se o campo "sub" não existir no payload, o token é inválido.
        if username is None:
            return None
        
        # Retorna os dados do payload validados pelo schema TokenData.
        return TokenData(username=username)
    except JWTError as e:
        print(f"DEBUG: JWTError decoding token: {e}")
        # Se qualquer erro de JWT ocorrer (assinatura inválida, expirado, etc.), retorna None.
        return None
