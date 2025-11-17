from typing import List, Optional
from fastapi import APIRouter, Depends, File, UploadFile, status, HTTPException, Query
from fastapi.responses import JSONResponse

from app.services.auth.user_token import get_current_user
from app.schemas.activity import ActivityCreate, ActivityResponse
from app.services.activities.activities_services import (
    create_activity_service,
    get_activity_service,
    update_activity_service,
    delete_activity_service,
    list_activities_service,
    filter_activities_service,
    change_activity_status,
    update_last_execution_service,
)
from app.services.utils import handle_image_update

router = APIRouter(prefix="/atividades", tags=["Atividades"])


@router.post(
    "/create", status_code=status.HTTP_201_CREATED, response_model=ActivityResponse
)
async def create_activity(
    request: ActivityCreate, user_doc: dict = Depends(get_current_user)
):
    """
    Cria uma nova atividade.

    Args:
        request (ActivityCreate): Dados da atividade a serem criados.
        user_doc (dict): Dados do funcionário que está criando a atividade

    Returns:
        ActivityResponse: Objeto contendo os dados da atividade criada.

    Raises:
        HTTPException: 500 em caso de erro interno do servidor.
    """
    try:
        data = create_activity_service(request, user_doc)
        return ActivityResponse(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor") from e


@router.get(
    "/list", status_code=status.HTTP_200_OK, response_model=List[ActivityResponse]
)
async def list_atividades(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_doc: dict = Depends(get_current_user),
):
    """
    Lista atividades de forma paginada.

    Args:
        skip (int, optional): Quantidade de registros a serem ignorados. Default é 0.
        limit (int, optional): Quantidade máxima de registros retornados. Default é 100.

    Returns:
        List[ActivityResponse]: Lista de atividades.

    Raises:
        HTTPException: 500 em caso de erro interno do servidor.
    """
    try:
        return list_activities_service(skip, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor") from e


@router.get(
    "/get/{ordem_servico}",
    status_code=status.HTTP_200_OK,
    response_model=ActivityResponse,
)
async def get_atividade(ordem_servico: int, user_doc: dict = Depends(get_current_user)):
    """
    Busca uma atividade pelo número da ordem de serviço.

    Args:
        ordem_servico (int): Número da ordem de serviço da atividade.

    Returns:
        ActivityResponse: Dados da atividade encontrada.

    Raises:
        HTTPException:
            404 se a atividade não for encontrada.
            500 em caso de erro interno do servidor.
    """
    atividade = get_activity_service(ordem_servico)
    if not atividade:
        raise HTTPException(
            status_code=404, detail=f"Atividade com OS {ordem_servico} não encontrada"
        )
    return ActivityResponse(**atividade)


@router.put(
    "/update/{ordem_servico}",
    status_code=status.HTTP_200_OK,
    response_model=ActivityResponse,
)
async def update_atividade(
    ordem_servico: int,
    request: ActivityCreate,
    user_doc: dict = Depends(get_current_user),
):
    """
    Atualiza uma atividade existente.

    Args:
        ordem_servico (int): Número da ordem de serviço da atividade.
        request (ActivityCreate): Dados atualizados da atividade.

    Returns:
        ActivityResponse: Dados atualizados da atividade.

    Raises:
        HTTPException: 500 em caso de erro interno do servidor.
    """
    try:
        updated = update_activity_service(ordem_servico, request)

        return ActivityResponse(**updated)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor") from e


@router.put(
    "/change-activity-image/{ordem_servico}",
    status_code=status.HTTP_200_OK,
)
async def change_activity_image(
    ordem_servico: int,
    file: UploadFile = File(),
    user_doc: dict = Depends(get_current_user),
):
    """
    Atualiza a imagem de uma atividade específica.

    Args:
        ordem_servico (int): Número da ordem de serviço da atividade.
        file (UploadFile): Arquivo de imagem a ser enviado.
        user_doc (dict): Documento do usuário autenticado.

    Returns:
        JSONResponse: Dados da imagem atualizada.

    Raises:
        HTTPException: 400 em caso de erro de validação ou 500 em erro interno do servidor.
    """
    try:
        image = await handle_image_update(file, "activity", user_doc, ordem_servico)
        return JSONResponse(image, 200)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor") from e


@router.delete("/delete/{ordem_servico}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_atividade(
    ordem_servico: int, user_doc: dict = Depends(get_current_user)
):
    """
    Remove uma atividade existente.

    Args:
        ordem_servico (int): Número da ordem de serviço da atividade.

    Returns:
        None: Resposta vazia (204 No Content).

    Raises:
        HTTPException: 500 em caso de erro interno do servidor.
    """
    try:
        delete_activity_service(ordem_servico)
        return
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor") from e


@router.get(
    "/filter/", status_code=status.HTTP_200_OK, response_model=List[ActivityResponse]
)
async def filter_atividades(
    tipo_manutencao: Optional[str] = None,
    departamento: Optional[str] = None,
    funcionario_criador: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    user_doc: dict = Depends(get_current_user),
):
    """
    Filtra atividades por campos opcionais.

    Args:
        tipo_manutencao (str, optional): Tipo de manutenção para filtro.
        departamento (str, optional): Departamento associado à atividade.
        funcionario_criador (str, optional): Funcionário criador da atividade.
        status (str, optional): status da atividade (Pendete, Concluída ou Agendada).
        skip (int, optional): Quantidade de registros a serem ignorados. Default é 0.
        limit (int, optional): Quantidade máxima de registros retornados. Default é 100.

    Returns:
        List[ActivityResponse]: Lista de atividades filtradas.

    Raises:
        HTTPException: 500 em caso de erro interno do servidor.
    """
    try:
        return filter_activities_service(
            tipo_manutencao, departamento, funcionario_criador, status, skip, limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor") from e


@router.patch(
    "/forward_activity/{ordem_servico}",
    status_code=status.HTTP_200_OK,
)
async def forward_activity(
    ordem_servico: int,
    user_doc: dict = Depends(get_current_user),
):
    """
    atualiza uma atividade com base na ordem de serviço informada.

    Args:
        ordem_servico (int): Número da ordem de serviço da atividade a ser finalizada.
        user_doc (dict): Documento do usuário autenticado.

    Returns:
        dict: status anterior e status atual da atividade atualizada

    Raises:
        HTTPException:
            - 409: Caso a atividade não possa ser finalizada (conflito de estado).
            - 500: Em caso de erro interno do servidor.
    """
    try:
        result = change_activity_status(ordem_servico)
        return result

    except HTTPException as e:
        # Mantém o status 409 e detalhe do erro original
        raise HTTPException(status_code=e.status_code, detail=e.detail) from e

    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor") from e
    

@router.patch(
    "/update-last-execution/{ordem_servico}",
    status_code=status.HTTP_200_OK,
    response_model=ActivityResponse,
)
async def update_last_execution(
    ordem_servico: int,
    user_doc: dict = Depends(get_current_user),
):
    """
    Atualiza apenas o campo 'ultima_execucao' de uma atividade com a data/hora atual UTC.

    Args:
        ordem_servico (int): Número da ordem de serviço da atividade.
        user_doc (dict): Dados do usuário autenticado (obtidos via dependência).

    Returns:
        ActivityResponse: Objeto contendo os dados da atividade atualizada.

    Raises:
        HTTPException: 404 se a atividade não for encontrada.
        HTTPException: 500 em caso de erro interno do servidor.
    """
    try:
        updated = update_last_execution_service(ordem_servico)
        return ActivityResponse(**updated)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor")