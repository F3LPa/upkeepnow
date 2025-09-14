from datetime import date, datetime, time
from typing import Literal
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class ActiveUserResponse(BaseModel):
    cpf: str
    dataCriacao: datetime
    nome: str
    email: EmailStr
    telefone: str
    dataNascimento: date
    departamento: str
    cargo: str
    inicioTurno: time
    fimTurno: time
    nivel: Literal["funcionario", "gestor", "mestre"]

    class Config:
        from_attributes = True
