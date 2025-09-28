from datetime import datetime, time
from typing import Optional
import sqlalchemy as sa
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy import Column

from app.db.base import Base
from app.models.atividade import Atividade


class Funcionario(Base):
    __tablename__ = "funcionarios"

    cpf: str = Column(sa.String(50), primary_key=True)
    data_criacao: datetime = Column(sa.DateTime, default=datetime.now, index=True)
    nome: str = Column(sa.String(100), nullable=False)
    email: str = Column(sa.String(150), nullable=False)
    telefone: str = Column(sa.String(20), nullable=False)
    data_nascimento: Optional[datetime] = Column(sa.Date, nullable=False)
    senha: str = Column(sa.String(200), nullable=False)
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


class FuncionarioF:
    def __init__(
        self,
        cpf: str,
        nome: str,
        email: str,
        telefone: str,
        data_nascimento: Optional[datetime],
        senha: str,
        departamento: Optional[str],
        cargo: str,
        inicio_turno: time,
        fim_turno: time,
        nivel: Optional[str],
    ):
        pass
