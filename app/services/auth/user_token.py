from datetime import datetime, timedelta

from jose import jwt

from sqlalchemy.orm import Session

from fastapi import Depends, HTTPException, logger, status
from fastapi.security import OAuth2PasswordBearer

from app.services.auth.security import verify_password
from app.models import Funcionario
from app.env_settings import settings
from app.db.firebase import firestore_db  # Import Firebase Firestore

SECRET_KEY: str = settings("SECRET_KEY")
ALGORITHM: str = settings("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 300

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
COLLECTION = "usuarios"


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
    expires = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    encode.update({"exp": expires})

    return jwt.encode(encode, key=SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)):
    """Decodifica o Token para validar autorização do usuário atual.

    Args:
        token (str): Token recebido via Bearer

    Raises:
        HTTPException: Caso a decodificação não encontre valores

    Returns:
        dict: Documento do Firebase do usuário
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

        # Busca o usuário no Firebase Firestore
        users_ref = firestore_db.collection(COLLECTION)
        query = (
            users_ref.where("email", "==", username.strip().lower())
            .where("cpf", "==", user_id)
            .limit(1)
            .get()
        )

        if not query:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        user_doc = query[0].to_dict()
        user_doc["id"] = query[0].id
        return user_doc

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Erro ao decodificar token ou buscar usuário: {exc}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar usuário: {exc}")


def require_role(cargo_requerido: str):
    """
    Verifica o nivel do usuario e se ele tem permissão para acessar determinado recurso

    Args:
        cargo str: Role necessária para acessar o endpoint
    """

    def role_checker(
        current_user: dict = Depends(get_current_user),
    ):
        if (
            not current_user.get("cargo")
            or current_user.get("cargo") != cargo_requerido
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão '{cargo_requerido}' necessária",
            )
        return current_user

    return role_checker
