import bcrypt


def hash_password(password: str) -> str:
    """Gera hash seguro com salt para a senha."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verifica senha em texto puro contra hash armazenado."""
    return bcrypt.checkpw(password.encode(), hashed.encode())
