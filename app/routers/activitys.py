from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, status, Depends, HTTPException, Query
from sqlalchemy import select
import sqlalchemy.exc as SqlExc
from firebase_admin.firestore import firestore

from app.schemas.activity import ActivityCreate, ActivityResponse
from app.db.db_session import create_session, Session
from app.models.atividade import Atividade
from app.db.firebase import firestore_db
from logger import logger


router = APIRouter(prefix="/atividades", tags=["Atividades"])


@router.post(
    "/create",
    description="Cria uma nova atividade",
    status_code=status.HTTP_201_CREATED,
    response_model=ActivityResponse,
)
async def create_atividade(
    request: ActivityCreate, db: Session = Depends(create_session)
):
    try:
        # Método mais direto usando ORM
        new_atividade_data = request.model_dump()
        atividade = Atividade(**new_atividade_data)

        db.add(atividade)
        db.commit()
        db.refresh(atividade)  # Garante que os dados estão atualizados

        logger.info(f"Atividade criada com sucesso: OS {atividade.ordem_servico}")
        return atividade

    except SqlExc.IntegrityError as exc:
        db.rollback()
        logger.error(f"Erro de integridade ao criar atividade: {exc}")
        raise HTTPException(
            status_code=400, detail="Dados inválidos ou funcionário não encontrado"
        ) from exc
    except SqlExc.SQLAlchemyError as exc:
        db.rollback()
        logger.error(f"Erro ao criar atividade no banco de dados: {exc}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor") from exc


@router.get(
    "/list",
    description="Lista todas as atividades com paginação",
    status_code=status.HTTP_200_OK,
    response_model=List[ActivityResponse],
)
async def list_atividades(
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(
        100, ge=1, le=1000, description="Número máximo de registros a retornar"
    ),
    db: Session = Depends(create_session),
):
    try:
        stmt = select(Atividade).offset(skip).limit(limit)
        result = db.execute(stmt).scalars().all()
        logger.info(f"Listadas {len(result)} atividades (skip={skip}, limit={limit})")
        return result
    except SqlExc.SQLAlchemyError as exc:
        logger.error(f"Erro ao listar atividades: {exc}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor") from exc


@router.get(
    "/get/{ordem_servico}",
    description="Busca uma atividade pelo número da ordem de serviço",
    status_code=status.HTTP_200_OK,
    response_model=ActivityResponse,
)
async def get_atividade(ordem_servico: int, db: Session = Depends(create_session)):
    try:
        atividade = db.get(Atividade, ordem_servico)
        if not atividade:
            logger.warning(f"Atividade não encontrada: OS {ordem_servico}")
            raise HTTPException(
                status_code=404,
                detail=f"Atividade com OS {ordem_servico} não encontrada",
            )
        logger.info(f"Atividade encontrada: OS {ordem_servico}")
        return atividade
    except HTTPException:
        raise  # Re-lança HTTPExceptions
    except SqlExc.SQLAlchemyError as exc:
        logger.error(f"Erro ao buscar atividade {ordem_servico}: {exc}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor") from exc


@router.put(
    "/update/{ordem_servico}",
    description="Atualiza uma atividade existente",
    status_code=status.HTTP_200_OK,
    response_model=ActivityResponse,
)
async def update_atividade(
    ordem_servico: int, request: ActivityCreate, db: Session = Depends(create_session)
):
    try:
        # Busca a atividade existente
        atividade = db.get(Atividade, ordem_servico)
        if not atividade:
            logger.warning(
                f"Tentativa de atualizar atividade inexistente: OS {ordem_servico}"
            )
            raise HTTPException(
                status_code=404,
                detail=f"Atividade com OS {ordem_servico} não encontrada",
            )

        # Atualiza os campos
        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(atividade, field, value)

        db.commit()
        db.refresh(atividade)

        logger.info(f"Atividade atualizada com sucesso: OS {ordem_servico}")
        return atividade

    except HTTPException:
        raise  # Re-lança HTTPExceptions
    except SqlExc.IntegrityError as exc:
        db.rollback()
        logger.error(
            f"Erro de integridade ao atualizar atividade {ordem_servico}: {exc}"
        )
        raise HTTPException(
            status_code=400, detail="Dados inválidos ou funcionário não encontrado"
        ) from exc
    except SqlExc.SQLAlchemyError as exc:
        db.rollback()
        logger.error(f"Erro ao atualizar atividade {ordem_servico}: {exc}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor") from exc


@router.delete(
    "/delete/{ordem_servico}",
    description="Remove uma atividade",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_atividade(ordem_servico: int, db: Session = Depends(create_session)):
    try:
        # Busca a atividade existente
        atividade = db.get(Atividade, ordem_servico)
        if not atividade:
            logger.warning(
                f"Tentativa de deletar atividade inexistente: OS {ordem_servico}"
            )
            raise HTTPException(
                status_code=404,
                detail=f"Atividade com OS {ordem_servico} não encontrada",
            )

        # Remove a atividade
        db.delete(atividade)
        db.commit()

        logger.info(f"Atividade removida com sucesso: OS {ordem_servico}")
        return  # 204 No Content não retorna body

    except HTTPException:
        raise  # Re-lança HTTPExceptions
    except SqlExc.SQLAlchemyError as exc:
        db.rollback()
        logger.error(f"Erro ao remover atividade {ordem_servico}: {exc}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor") from exc


# Rota adicional para buscar atividades por filtros
@router.get(
    "/filter/",
    description="Busca atividades por filtros específicos",
    status_code=status.HTTP_200_OK,
    response_model=List[ActivityResponse],
)
async def filter_atividades(
    tipo_manutencao: Optional[str] = Query(
        None, description="Filtrar por tipo de manutenção"
    ),
    departamento: Optional[str] = Query(None, description="Filtrar por departamento"),
    funcionario_criador: Optional[str] = Query(
        None, description="Filtrar por funcionário criador"
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(create_session),
):
    try:
        stmt = select(Atividade)

        # Aplica filtros se fornecidos
        if tipo_manutencao:
            stmt = stmt.where(Atividade.tipo_manutencao == tipo_manutencao)
        if departamento:
            stmt = stmt.where(Atividade.departamento == departamento)
        if funcionario_criador:
            stmt = stmt.where(Atividade.funcionario_criador == funcionario_criador)

        stmt = stmt.offset(skip).limit(limit)
        result = db.execute(stmt).scalars().all()

        logger.info(f"Filtro aplicado: {len(result)} atividades encontradas")
        return result

    except SqlExc.SQLAlchemyError as exc:
        logger.error(f"Erro ao filtrar atividades: {exc}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor") from exc


