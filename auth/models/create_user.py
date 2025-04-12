from datetime import datetime
from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    cpf: str
    data_criacao: datetime
    nome: str
    email: str
    telefone: str
    data_nascimento: str
    login: str
    senha: str
