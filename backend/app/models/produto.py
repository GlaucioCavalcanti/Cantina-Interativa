"""
Modelo ORM de Produto.

Representa a tabela 'produtos' no banco de dados com validações e relacionamentos.
"""

from sqlalchemy import Column, Integer, String, Float
from backend.app.core.database import Base


class Produto(Base):
    """
    Modelo ORM para a tabela de produtos (cardápio).
    
    Atributos:
        id: Identificador único do produto
        nome: Nome do produto/item do cardápio
        preco: Preço do produto em formato decimal
        descricao: Descrição detalhada (ingredientes, tamanho, etc)
    """
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False)
    preco = Column(Float, nullable=False)
    descricao = Column(String(500), nullable=False)

    def __repr__(self):
        return f"<Produto(id={self.id}, nome='{self.nome}', preco={self.preco})>"
