from datetime import date, datetime, time
from typing import Literal
from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginUserResponse(BaseModel):
    cpf: str
    data_criacao: datetime
    nome: str
    email: EmailStr
    telefone: str
    data_nascimento: date
    departamento:str
    cargo: str
    inicio_turno: time
    fim_turno: time
    nivel: Literal["funcionario", "gestor", "mestre"]

    class Config:
        from_attributes = True

    