"""
Schemas (Pydantic Models) para validação de requisições e respostas.

Os schemas são modelos de validação usados para serializar/desserializar
dados em requisições HTTP. Eles são separados dos modelos ORM (Database Models)
para maior flexibilidade e segurança.

Convenção:
- ClienteCreate: para criação (POST)
- ClienteUpdate: para atualização (PUT/PATCH)
- ClienteRead: para leitura/resposta (GET)
"""

from pydantic import BaseModel, EmailStr
from typing import Optional


# ==========================================
# CLIENTE SCHEMAS
# ==========================================

class ClienteCreate(BaseModel):
    """Schema para criação de cliente."""
    nome: str
    email: EmailStr


class ClienteUpdate(BaseModel):
    """Schema para atualização de cliente."""
    nome: Optional[str] = None
    email: Optional[EmailStr] = None


class ClienteRead(BaseModel):
    """Schema para leitura de cliente com dados do banco."""
    id: int
    nome: str
    email: str

    class Config:
        from_attributes = True  # Permite converter modelos ORM para este schema


# ==========================================
# PRODUTO SCHEMAS
# ==========================================

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
        from_attributes = True  # Permite converter modelos ORM para este schema
