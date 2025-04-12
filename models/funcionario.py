import sqlalchemy as sa
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy import Column

from datetime import datetime, time
from typing import List, Optional

from models.model_base import Base
from models.atividade import Atividade


class Funcionario(Base):
    __tablename__ = "funcionarios"

    cpf: str = Column(sa.String(50), primary_key=True)
    data_criacao: datetime = Column(sa.DateTime, default=datetime.now, index=True)
    nome: str = Column(sa.String(100), nullable=False)
    email: str = Column(sa.String(150), nullable=False)
    telefone: str = Column(sa.String(20), nullable=False)
    data_nascimento: Optional[datetime] = Column(sa.Date, nullable=False)
    login: str = Column(sa.String(30), nullable=False)
    senha: str = Column(sa.String(30), nullable=False)
    departamento: Optional[str] = Column(sa.String(20))
    cargo: Optional[str] = Column(sa.String(30))
    inicio_turno: time = Column(sa.Time)
    fim_turno: time = Column(sa.Time)
    nivel: Optional[str] = Column(sa.Enum("funcionario", "gestor", "mestre"))

    atividades_criadas: Mapped[Atividade] = relationship(
        "Atividade", back_populates="criador"
    )

    def __repr__(self):
        return (
            f"<Funcionario(cpf='{self.cpf}', nome='{self.nome}', nivel='{self.nivel}')>"
        )
