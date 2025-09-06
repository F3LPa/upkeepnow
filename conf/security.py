from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """criptografa senha

    Args:
        password (str): senha passada

    Returns:
        str: senha criptografada
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """verifica se senha bate com oque está no banco

    Args:
        plain_password (str): senha sem criptografia
        hashed_password (str): senha com criptografia

    Returns:
        bool: verdadeiro para senha autentica, falso para senha incorreta
    """
    return pwd_context.verify(plain_password, hashed_password)
