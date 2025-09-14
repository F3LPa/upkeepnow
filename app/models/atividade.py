import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy import Column

from datetime import datetime
from typing import Optional

from app.db.base import Base


class Atividade(Base):
    __tablename__ = "atividades"

    ordem_servico: int = Column(sa.Integer, primary_key=True)
    nome: str = Column(sa.String(50), nullable=False)
    departamento: Optional[str] = Column(sa.String(30))
    tipo_manutencao: str = Column(
        sa.Enum("corretiva", "preditiva", "preventiva"), nullable=False
    )
    data_abertura: datetime = Column(sa.TIMESTAMP, nullable=False)
    data_fechamento: datetime = Column(sa.TIMESTAMP, nullable=False)
    prioridade: int = Column(sa.Integer, nullable=False)
    descricao: str = Column(sa.Text)
    funcionario_criador: str = Column(
        sa.String(50), sa.ForeignKey("funcionarios.cpf"), nullable=False
    )

    criador = relationship("Funcionario", back_populates="atividades_criadas")

    def __repr__(self):
        return f"<Atividade(ordem_servico={self.ordem_servico}, nome='{self.nome}', tipo='{self.tipo_manutencao}')>"
