import os
from typing import Any
from dotenv import load_dotenv
from logger import logger

# Carrega as variáveis de ambiente do arquivo .env (se existir)
load_dotenv()


def settings(key: str) -> Any:
    """
    Obtém o valor de uma variável de ambiente específica.
    Args:
        key: Nome da variável de ambiente
    Returns:
        Valor da variável de ambiente ou o valor padrão
    """
    try:
        env_var = os.getenv(key)

        return env_var

    except AttributeError:
        logger.error(f"Não foi possível buscar a variavel de ambiente: {key}")
