from app.db.firebase import firestore_db

COLLECTION = "atividades"
COUNTER_DOC = "counters/atividades"


def get_next_ordem_servico():
    """
    Recupera e incrementa o último número de ordem de serviço.

    Returns:
        int: Novo valor da ordem de serviço (incrementado).
    """
    counter_ref = firestore_db.document(COUNTER_DOC)
    counter_snapshot = counter_ref.get()
    if counter_snapshot.exists:
        ordem_servico = counter_snapshot.to_dict().get("last_id", 0) + 1
    else:
        ordem_servico = 1
    counter_ref.set({"last_id": ordem_servico})
    return ordem_servico


def create_activity(data: dict, ordem_servico: int):
    """
    Salva uma nova atividade no Firestore.

    Args:
        data (dict): Dados da atividade a serem salvos.
        ordem_servico (int): Número da ordem de serviço atribuída.

    Returns:
        dict: Dados da atividade criada, incluindo o campo `ordem_servico`.
    """
    data["ordem_servico"] = ordem_servico
    firestore_db.collection(COLLECTION).document(str(ordem_servico)).set(data)
    return data


def get_activity(ordem_servico: int):
    """
    Recupera uma atividade pelo número da ordem de serviço.

    Args:
        ordem_servico (int): Número da ordem de serviço da atividade.

    Returns:
        DocumentSnapshot | None: Documento da atividade, ou None se não encontrada.
    """
    doc = firestore_db.collection(COLLECTION).document(str(ordem_servico)).get()
    return doc if doc.exists else None


def update_activity(ordem_servico: int, data: dict):
    """
    Atualiza os campos de uma atividade existente.

    Args:
        ordem_servico (int): Número da ordem de serviço da atividade.
        data (dict): Campos a serem atualizados.

    Returns:
        dict: Dados atualizados da atividade.
    """
    doc_ref = firestore_db.collection(COLLECTION).document(str(ordem_servico))
    doc_ref.update(data)
    return doc_ref.get().to_dict()


def delete_activity(ordem_servico: int):
    """
    Remove uma atividade do Firestore.

    Args:
        ordem_servico (int): Número da ordem de serviço da atividade a ser removida.
    """
    firestore_db.collection(COLLECTION).document(str(ordem_servico)).delete()


def list_activities(skip: int = 0, limit: int = 100):
    """
    Lista atividades de forma paginada, ordenadas pelo campo `ordem_servico`.

    Args:
        skip (int, optional): Quantidade de registros a serem ignorados. Default é 0.
        limit (int, optional): Quantidade máxima de registros retornados. Default é 100.

    Returns:
        list[dict]: Lista de atividades em formato de dicionário.
    """
    docs = (
        firestore_db.collection(COLLECTION)
        .order_by("ordem_servico")
        .offset(skip)
        .limit(limit)
        .stream()
    )
    return [doc.to_dict() for doc in docs]


def filter_activities(filters: dict, skip: int = 0, limit: int = 100):
    """
    Aplica filtros opcionais à coleção de atividades e retorna resultados paginados.

    Args:
        filters (dict): Dicionário contendo os campos e valores para filtragem.
        skip (int, optional): Quantidade de registros a serem ignorados. Default é 0.
        limit (int, optional): Quantidade máxima de registros retornados. Default é 100.

    Returns:
        list[dict]: Lista de atividades filtradas em formato de dicionário.
    """
    query = firestore_db.collection(COLLECTION)
    for key, value in filters.items():
        if value:
            query = query.where(key, "==", value)
    docs = query.offset(skip).limit(limit).stream()
    return [doc.to_dict() for doc in docs]
