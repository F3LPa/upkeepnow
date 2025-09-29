from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class ActivityCreate(BaseModel):
    nome: str = Field(..., max_length=50)
    departamento: Optional[str] = Field(None, max_length=30)
    tipo_manutencao: Literal["corretiva", "preditiva", "preventiva"]
    data_abertura: datetime
    data_fechamento: Optional[datetime] = None
    prioridade: int = Field(..., ge=1, le=5)
    descricao: Optional[str] = None
    funcionario_criador: str = Field(..., max_length=50)


class ActivityResponse(BaseModel):
    ordem_servico: int
    nome: str
    departamento: Optional[str]
    tipo_manutencao: str
    data_abertura: datetime
    data_fechamento: Optional[datetime]
    prioridade: int
    descricao: Optional[str]
    funcionario_criador: str
