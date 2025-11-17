from datetime import datetime, time
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr


class CreateUserRequest(BaseModel):
    cpf: str
    nome: str
    email: EmailStr
    telefone: str
    dataNascimento: datetime
    senha: str
    gestorResponsavel: Optional[str] = None
    departamento: str
    cargo: str
    inicioTurno: time
    fimTurno: time
    nivel: Literal["funcionario", "gestor", "mestre"]

class UpdateUserRequest(BaseModel):
    cpf: str
    nome: str
    email: EmailStr
    telefone: str
    dataNascimento: datetime
    senha: Optional[str] = None
    gestorResponsavel: Optional[str] = None
    departamento: str
    cargo: str
    inicioTurno: time
    fimTurno: time
    nivel: Literal["funcionario", "gestor", "mestre"]
