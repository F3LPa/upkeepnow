from app.db.firebase import firestore_db

COLLECTION = "usuarios"


def get_user_by_email(email: str):
    """
    Busca um usuário no Firestore pelo email.

    Args:
        email (str): Email do usuário a ser buscado.

    Returns:
        DocumentSnapshot | None: Retorna o documento do usuário se encontrado,
        caso contrário retorna None.
    """
    query = (
        firestore_db.collection(COLLECTION)
        .where("email", "==", email.strip().lower())
        .limit(1)
        .get()
    )
    if not query:
        return None
    return query[0]


def get_users():
    """
    Busca usuários no Firestore.

    Returns:
        QueryResultsList | None: Retorna lista de documentos dos usuários se encontrado,
        caso contrário retorna None.
    """
    query = firestore_db.collection(COLLECTION).get()

    if not query:
        return None

    return query


def add_user(user_data: dict):
    """
    Adiciona um novo usuário no Firestore.

    Args:
        user_data (dict): Dicionário contendo os dados do usuário.

    Returns:
        None
    """
    firestore_db.collection(COLLECTION).add(user_data)


def update_user_data(user_id: str, data: dict):
    """
    Atualiza os dados de um usuário existente no Firestore.

    Args:
        user_id (str): ID do documento do usuário no Firestore.
        data (dict): Dicionário com os campos a serem atualizados.

    Returns:
        None
    """
    firestore_db.collection(COLLECTION).document(user_id).update(data)


def delete_user(user_id: str):
    """
    Deleta um usuário do Firestore pelo ID do documento.

    Args:
        user_id (str): ID do documento do usuário no Firestore.

    Returns:
        None
    """
    firestore_db.collection(COLLECTION).document(user_id).delete()
