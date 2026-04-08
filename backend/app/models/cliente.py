"""
Modelo ORM de Cliente.

Representa a tabela 'clientes' no banco de dados com validações e relacionamentos.
"""

from sqlalchemy import Column, Integer, String
from backend.app.core.database import Base


class Cliente(Base):
    """
    Modelo ORM para a tabela de clientes.
    
    Atributos:
        id: Identificador único do cliente
        nome: Nome completo do cliente
        email: Email único do cliente (índice único para integridade de dados)
    """
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)

    def __repr__(self):
        return f"<Cliente(id={self.id}, nome='{self.nome}', email='{self.email}')>"
