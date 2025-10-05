from logger import logger
from .activitys_repositories import (
    get_next_ordem_servico,
    create_activity,
    get_activity,
    update_activity,
    delete_activity,
    list_activities,
    filter_activities,
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
    skip: int = 0,
    limit: int = 100,
):
    """
    Filtra atividades por critérios opcionais e retorna os resultados paginados.

    Args:
        tipo_manutencao (str, optional): Tipo de manutenção para filtrar.
        departamento (str, optional): Departamento responsável pela atividade.
        funcionario_criador (str, optional): Identificação do funcionário criador.
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
        }
        atividades = filter_activities(filters, skip, limit)
        logger.info(f"Filtro aplicado: {len(atividades)} atividades encontradas")
        return atividades
    except Exception as e:
        logger.error(f"Erro ao filtrar atividades: {e}")
        raise e
