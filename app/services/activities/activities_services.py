from datetime import datetime
from fastapi import HTTPException

from app.services.chat.chat_service import ChatService
from logger import logger
from .activities_repositories import (
    get_next_ordem_servico,
    create_activity,
    get_activity,
    update_activity,
    delete_activity,
    list_activities,
    filter_activities,
    update_last_execution,
)
from app.schemas.activity import ActivityCreate


def create_activity_service(request: ActivityCreate, user_doc: dict):
    """
    Cria uma nova atividade no banco de dados.

    Args:
        request (ActivityCreate): Objeto contendo os dados da atividade a ser criada.
        user_doc (dict): Dados do funcionário que está criando a atividade

    Returns:
        dict: Dados da atividade criada, incluindo o número da ordem de serviço.

    Raises:
        Exception: Se ocorrer um erro durante a criação da atividade.
    """
    try:
        data = request.model_dump()
        ordem_servico = get_next_ordem_servico()
        created = create_activity(data, ordem_servico, user_doc)
        logger.info(f"Atividade criada com sucesso: OS {ordem_servico}")
        return created
    except Exception as e:
        logger.error(f"Erro ao criar atividade: {e}")
        raise e


def get_activity_service(ordem_servico: int):
    """
    Busca uma atividade pelo número da ordem de serviço.

    Args:
        ordem_servico (int): Número da ordem de serviço da atividade.

    Returns:
        dict | None: Dados da atividade, ou None se não for encontrada.
    """
    doc = get_activity(ordem_servico)
    if not doc:
        return None
    return doc.to_dict()


def update_activity_service(ordem_servico: int, request: ActivityCreate):
    """
    Atualiza uma atividade existente no banco de dados.

    Args:
        ordem_servico (int): Número da ordem de serviço da atividade.
        request (ActivityCreate): Dados atualizados da atividade.

    Returns:
        dict: Dados da atividade atualizada.

    Raises:
        Exception: Se ocorrer um erro durante a atualização.
    """
    try:
        data = request.model_dump(exclude_unset=True)
        updated = update_activity(ordem_servico, data)
        logger.info(f"Atividade atualizada com sucesso: OS {ordem_servico}")
        return updated
    except Exception as e:
        logger.error(f"Erro ao atualizar atividade {ordem_servico}: {e}")
        raise e


def delete_activity_service(ordem_servico: int):
    """
    Remove uma atividade do banco de dados.

    Args:
        ordem_servico (int): Número da ordem de serviço da atividade.

    Raises:
        Exception: Se ocorrer um erro durante a exclusão.
    """
    try:
        delete_activity(ordem_servico)
        logger.info(f"Atividade removida com sucesso: OS {ordem_servico}")
    except Exception as e:
        logger.error(f"Erro ao remover atividade {ordem_servico}: {e}")
        raise e


def list_activities_service(skip: int = 0, limit: int = 100):
    """
    Lista atividades paginadas do banco de dados.

    Args:
        skip (int, optional): Quantidade de registros a serem ignorados. Default é 0.
        limit (int, optional): Quantidade máxima de registros a serem retornados. Default é 100.

    Returns:
        list: Lista de atividades.

    Raises:
        Exception: Se ocorrer um erro durante a listagem.
    """
    try:
        activities = list_activities(skip, limit)
        logger.info(f"Listadas {len(activities)} atividades")
        return activities
    except Exception as e:
        logger.error(f"Erro ao listar atividades: {e}")
        raise e


def filter_activities_service(
    tipo_manutencao: str = None,
    departamento: str = None,
    funcionario_criador: str = None,
    status: str = None,
    skip: int = 0,
    limit: int = 100,
):
    """
    Filtra atividades por critérios opcionais e retorna os resultados paginados.

    Args:
        tipo_manutencao (str, optional): Tipo de manutenção para filtrar.
        departamento (str, optional): Departamento responsável pela atividade.
        funcionario_criador (str, optional): Identificação do funcionário criador.
        status (str, optional): status da atividade (Pendete, Concluída ou Agendada).
        skip (int, optional): Quantidade de registros a serem ignorados. Default é 0.
        limit (int, optional): Quantidade máxima de registros retornados. Default é 100.

    Returns:
        list: Lista de atividades filtradas.

    Raises:
        Exception: Se ocorrer um erro durante a filtragem.
    """
    try:
        filters = {
            "tipo_manutencao": tipo_manutencao,
            "departamento": departamento,
            "funcionario_criador": funcionario_criador,
            "status": status,
        }

        atividades = filter_activities(filters, skip, limit)
        logger.info(f"Filtro aplicado: {len(atividades)} atividades encontradas")
        return atividades
    except Exception as e:
        logger.error(f"Erro ao filtrar atividades: {e}")
        raise e


def change_activity_status(ordem_servico: int) -> None:
    """
    Finaliza uma atividade existente com base na ordem de serviço informada.

    Verifica se a atividade já foi finalizada. Caso não tenha sido,
    atualiza o campo `data_fechamento` com a data e hora atuais.
    Também deleta o chat associado caso a atividade seja concluída.

    Args:
        ordem_servico (int): Número da ordem de serviço da atividade a ser finalizada.

    Raises:
        HTTPException:
            - 409: Caso a atividade já tenha sido finalizada anteriormente.
            - 404: Caso a atividade não exista (caso `get_activity` lance este erro).
            - 500: Em caso de erro interno ao atualizar a atividade.
    """
    from app.services.chat.chat_service import ChatService

    activity = get_activity(ordem_servico)
    activity_status = activity.to_dict()["status"]
    chat_service = ChatService()

    if activity_status == "Pendente":
        updated = update_activity(ordem_servico, {"status": "Em andamento"})

    elif activity_status == "Em andamento":
        updated = update_activity(
            ordem_servico, {"status": "Concluída", "data_fechamento": datetime.now()}
        )
        _delete_associated_chat(chat_service, ordem_servico, activity)

    elif activity_status == "Agendada":
        updated = update_activity(
            ordem_servico, {"status": "Concluída", "data_fechamento": datetime.now()}
        )
        _delete_associated_chat(chat_service, ordem_servico, activity)

    elif activity_status == "Concluída":
        raise HTTPException(status_code=409, detail="Atividade já foi finalizada")

    else:
        raise HTTPException(status_code=500, detail="Atividade não pode ser atualizada")

    return {"status_anterior": activity_status, "status_atual": updated["status"]}


def _delete_associated_chat(
    chat_service: ChatService, ordem_servico: int, activity
) -> None:
    """
    Função auxiliar para deletar o chat associado a uma ordem de serviço.
    """
    try:
        # Busca o chat associado à ordem de serviço
        chat = chat_service.get_chat_by_ordem_servico(ordem_servico)

        if chat:
            # Pega o documento completo da atividade
            activity_data = activity.to_dict()

            # Tenta diferentes campos possíveis para o owner
            owner = (
                activity_data.get("criador")
                or activity_data.get("cpf_responsavel")
                or activity_data.get("cpf_tecnico")
                or chat.get("criador")  # Usa o criador do próprio chat como fallback
            )

            chat_service.delete_chat(chat["id"], owner)

    except HTTPException as e:
        if e.status_code == 404:
            raise e
    except Exception as e:
        raise e

def update_last_execution_service(ordem_servico: int) -> dict:
    """
    Atualiza apenas o campo 'ultima_execucao' de uma atividade diretamente na coleção.

    Args:
        ordem_servico (int): Número da ordem de serviço da atividade.

    Returns:
        dict: Dados atualizados da atividade.

    Raises:
        ValueError: Se a atividade não for encontrada.
        Exception: Se ocorrer erro durante a atualização.
    """
    activity = get_activity(ordem_servico)
    if not activity:
        raise ValueError(f"Atividade com OS {ordem_servico} não encontrada")

    return update_last_execution(ordem_servico)
