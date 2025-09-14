from typing import Annotated
from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import insert
import sqlalchemy.exc as SqlExc

from app.schemas.auth.create_user import CreateUserRequest
from app.schemas.auth.login_user import ActiveUserResponse, Token
from app.auth.user_token import create_access_token, get_current_user, user_authenticate
from app.db.db_session import create_session, Session
from app.auth.security import hash_password
from app.models.funcionario import Funcionario
from logger import logger


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/create_user", description="cria usuario", status_code=status.HTTP_201_CREATED
)
async def create_user(
    request: CreateUserRequest, db: Session = Depends(create_session)
):
    try:
        validate_user = (
            db.query(Funcionario).filter(Funcionario.email == request.email).first()
        )

        if validate_user:
            logger.error("Erro: Usuário já existente")
            raise HTTPException(409, "Erro: Usuário já existente")
        else:
            new_user_data = request.model_dump()
            new_user_data["senha"] = hash_password(request.senha)
            insert_script = insert(Funcionario).values(new_user_data)
            db.execute(insert_script)

            db.flush()
            db.commit()
            db.close()
            logger.info("Usuário criado com sucesso")

    except SqlExc.SQLAlchemyError as exc:
        logger.error("Erro ao criar usuário no banco de dados")
        raise SqlExc.SQLAlchemyError from exc


@router.post(
    "/login",
    description="Faz login",
    status_code=status.HTTP_200_OK,
    response_model=Token,
)
async def login(
    request: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(create_session),
):
    try:
        user: Funcionario = user_authenticate(request.username, request.password, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = create_access_token(user.email, user.cpf)

        return {"access_token": token, "token_type": "bearer"}
    except SqlExc.SQLAlchemyError as exc:
        logger.error("Erro ao tentar fazer login")
        raise exc


@router.get(
    "/current_user",
    description="Busca usuário atual",
    status_code=status.HTTP_200_OK,
    response_model=ActiveUserResponse,
)
async def current_user(user: Funcionario = Depends(get_current_user)):
    return {
        "cpf": user.cpf,
        "dataCriacao": user.data_criacao,
        "nome": user.nome,
        "email": user.email,
        "telefone": user.telefone,
        "dataNascimento": user.data_nascimento,
        "departamento": user.departamento,
        "cargo": user.cargo,
        "inicioTurno": user.inicio_turno,
        "fimTurno": user.fim_turno,
        "nivel": user.nivel,
    }
