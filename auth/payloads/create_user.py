from datetime import date, datetime, time
from typing import Literal
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext


class CreateUserRequest(BaseModel):
    cpf: str
    nome: str
    email: EmailStr
    telefone: str
    data_nascimento: date
    senha: str
    departamento:str
    cargo: str
    inicio_turno: time
    fim_turno: time
    nivel: Literal["funcionario", "gestor", "mestre"]