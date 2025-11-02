from datetime import datetime
from app.services.auth.auth_repositories import (
    get_user_by_email,
    get_users,
    add_user,
    update_user_data,
    delete_user,
)
from app.services.auth.auth_utils import hash_password, verify_password
from logger import logger


def create_user_service(user_data: dict):
    """
    Cria um novo usuário no Firestore.

    Realiza validação de email duplicado, normaliza dados, faz hash da senha,
    adiciona data de criação e salva o usuário.

    Args:
        user_data (dict): Dicionário contendo os dados do usuário, incluindo:
            - email (str)
            - senha (str)
            - inicioTurno (datetime.time)
            - fimTurno (datetime.time)
            - outros campos opcionais

    Raises:
        ValueError: Se o usuário com o email informado já existir.

    Returns:
        dict: Mensagem de sucesso.
    """
    if get_user_by_email(user_data["email"]):
        raise ValueError("Usuário já existente")

    user_data["email"] = user_data["email"].strip().lower()
    user_data["inicioTurno"] = user_data["inicioTurno"].strftime("%H:%M:%S")
    user_data["fimTurno"] = user_data["fimTurno"].strftime("%H:%M:%S")
    user_data["senha"] = hash_password(user_data["senha"])
    user_data["dataCriacao"] = datetime.now()

    add_user(user_data)
    logger.info(f"Usuário {user_data['email']} criado com sucesso")
    return {"msg": "Usuário criado com sucesso"}


def login_user_service(user_email: str, password: str):
    """
    Autentica um usuário, gera um token JWT e retorna os dados do usuário (sem a senha).

    Args:
        user_email (str): Email do usuário.
        password (str): Senha do usuário.

    Raises:
        ValueError: Se as credenciais forem inválidas.

    Returns:
        dict: Contendo 'access_token', 'token_type' e 'user' com os dados do usuário.
    """
    from app.services.auth.user_token import create_access_token

    user_doc = get_user_by_email(user_email)
    if not user_doc:
        raise ValueError("Credenciais inválidas")

    user_dict = user_doc.to_dict()
    if not user_dict.get("senha") or not verify_password(password, user_dict["senha"]):
        raise ValueError("Credenciais inválidas")

    # Gerar token
    token = create_access_token(user_dict["email"], user_dict.get("cpf", ""))

    # Remover a senha antes de retornar os dados do usuário
    user_dict.pop("senha", None)

    return {"access_token": token, "token_type": "bearer", "user": user_dict}


def update_user_service(user_doc: dict, updated_data):
    """
    Atualiza os dados de um usuário existente.

    Normaliza email, converte horários, realiza hash da senha se necessário
    e atualiza o documento no Firestore.

    Args:
        user_doc (dict): Dicionário com os dados do usuário autenticado, incluindo 'id'.
        updated_data: Objeto Pydantic com os novos dados do usuário.

    Returns:
        dict: Mensagem de sucesso.
    """
    data = updated_data.model_dump()
    data["email"] = data["email"].strip().lower()
    data["inicioTurno"] = data["inicioTurno"].strftime("%H:%M:%S")
    data["fimTurno"] = data["fimTurno"].strftime("%H:%M:%S")
    if "senha" in data:
        data["senha"] = hash_password(data["senha"])

    update_user_data(user_doc["id"], data)
    logger.info(f"Usuário {user_doc['email']} atualizado com sucesso")
    return {"msg": "Usuário atualizado com sucesso"}


def delete_user_service(user_doc: dict):
    """
    Deleta um usuário do Firestore.

    Verifica se o usuário existe pelo email e deleta o documento correspondente.

    Args:
        user_doc (dict): Dicionário com os dados do usuário autenticado, incluindo 'email'.

    Raises:
        ValueError: Se o usuário não for encontrado.

    Returns:
        dict: Mensagem de sucesso.
    """
    user_email = user_doc.get("email")
    user_record = get_user_by_email(user_email)
    if not user_record:
        raise ValueError("Usuário não encontrado")
    delete_user(user_record.id)
    logger.info(f"Usuário {user_email} deletado com sucesso")
    return {"msg": "Usuário deletado com sucesso"}


def get_all_users():
    users_ref = get_users()

    users = []

    for user_ref in users_ref:
        users.append(user_ref.to_dict())

    return users


def get_user(email: str):
    users_ref = get_user_by_email(email)

    return users_ref.to_dict()
