from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class ActivityCreate(BaseModel):
    nome: str = Field(..., max_length=50)
    departamento: Optional[str] = Field(None, max_length=30)
    tipo_manutencao: Literal["Corretiva", "Preditiva", "Preventiva"]
    localizacao: str
    data_abertura: datetime
    data_fechamento: Optional[datetime] = None
    prioridade: Literal["Baixa", "Média", "Alta", "Urgente"]
    descricao: Optional[str] = None


class ActivityResponse(BaseModel):
    ordem_servico: int
    nome: str
    departamento: Optional[str]
    tipo_manutencao: str
    localizacao: str
    data_abertura: datetime
    data_fechamento: Optional[datetime]
    prioridade: str
    descricao: Optional[str]
    funcionario_criador: str
    image_url: Optional[str] = None
