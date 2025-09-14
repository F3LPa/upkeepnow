from datetime import date, time
from typing import Literal
from pydantic import BaseModel, EmailStr


class CreateUserRequest(BaseModel):
    cpf: str
    nome: str
    email: EmailStr
    telefone: str
    dataNascimento: date
    senha: str
    departamento: str
    cargo: str
    inicioTurno: time
    fimTurno: time
    nivel: Literal["funcionario", "gestor", "mestre"]
