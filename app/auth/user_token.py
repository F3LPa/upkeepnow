from datetime import datetime, timedelta

from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError

from sqlalchemy.orm import Session

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.conf.db_session import create_session
from app.auth.security import verify_password
from app.models import Funcionario
from env_settings import settings

SECRET_KEY: str = settings("SECRET_KEY")
ALGORITHM: str = settings("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 300

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def user_authenticate(email: str, password, db: Session) -> Funcionario:
    """Autentica as informações passadas nos argumentos

    Args:
        email (str): email do usuario
        password (str): senha do usuario
        db (Session): sessão do banco de dados que será utilizada para validar as informacoes

    Returns:
        Funcionario: classe ORM da entidade FUNCIONARIO do banco de dados
    """
    user = db.query(Funcionario).filter(Funcionario.email == email).first()

    if not user or not verify_password(password, user.senha):
        return False
    return user


def create_access_token(username: str, cpf: str):
    """Cria token de acesso JWT para autorizacao

    Args:
        username (str): login do usuario (no nosso caso o e-mail)
        cpf (str): Identificador da entidade FUNCIONARIO

    Returns:
        str: Token JWT
    """
    encode = {"sub": username, "id": cpf, "type": "access_token"}
    expires = datetime.now() + timedelta(ACCESS_TOKEN_EXPIRE_MINUTES)
    encode.update({"exp": expires})

    return jwt.encode(encode, key=SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(create_session)
) -> Funcionario:
    """Decodifica o Token para validar autorizacao do sessão atual do usuário

    Args:
        token (Annotated[str, oauth2__bearer]): Token recebido

    Raises:
        HTTPException: Caso a decodificacao não encontre valores

    Returns:
        dict: Com email e cpf do Usuario

    """
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: str = payload.get("id")

        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário Inválido"
            )

        if payload.get("type") != "access_token":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tipo de token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )

        exp = payload.get("exp")
        if exp and datetime.now() > datetime.fromtimestamp(exp):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = (
            db.query(Funcionario)
            .filter(Funcionario.email == username, Funcionario.cpf == user_id)
            .first()
        )

        return user

    except ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falha na validação do token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def require_role(cargo_requerido: str):
    """
    Verifica o nivel do usuario e se ele tem permissão para acessar determinado recurso

    Args:
        cargo str: Role necessária para acessar o endpoint
    """

    def role_checker(
        current_user: Funcionario = Depends(get_current_user),
    ) -> Funcionario:
        if not hasattr(current_user, "cargo") or current_user.cargo != cargo_requerido:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão '{cargo_requerido}' necessária",
            )
        return current_user

    return role_checker
