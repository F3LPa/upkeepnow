from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy import insert
import sqlalchemy.exc as SqlExc
from auth.models.create_user import CreateUserRequest
from conf.db_session import create_session, Session
from models.funcionario import Funcionario
from logger import logger

router = APIRouter(prefix="/auth")


@router.post(
    "/create_user", description="cria usuario", status_code=status.HTTP_201_CREATED
)
def create_user(
    request: CreateUserRequest, db_session: Session = Depends(create_session)
):
    try:
        validate_user = (
            db_session.query(Funcionario)
            .filter(
                Funcionario.login == request.login, Funcionario.senha == request.senha
            )
            .first()
        )

        logger.info(f"Criando usuário: {validate_user}")
        if validate_user:
            logger.error("Erro: Usuário já existente")
            raise HTTPException(409, "Erro: Usuário já existente")
        else:
            insert_script = insert(Funcionario).values(request.model_dump())
            db_session.execute(insert_script)

            db_session.flush()
            db_session.commit()

    except SqlExc.SQLAlchemyError as exc:
        logger.error("Erro ao criar usuário no banco de dados")
        raise SqlExc.SQLAlchemyError from exc
