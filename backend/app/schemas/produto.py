"""
Schemas de Produto para validação e serialização de dados.
"""

from pydantic import BaseModel
from typing import Optional


class ProdutoCreate(BaseModel):
    """Schema para criação de produto."""
    nome: str
    preco: float
    descricao: str


class ProdutoUpdate(BaseModel):
    """Schema para atualização de produto."""
    nome: Optional[str] = None
    preco: Optional[float] = None
    descricao: Optional[str] = None


class ProdutoRead(BaseModel):
    """Schema para leitura de produto com dados do banco."""
    id: int
    nome: str
    preco: float
    descricao: str

    class Config:
        from_attributes = True
