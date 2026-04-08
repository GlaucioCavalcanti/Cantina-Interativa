"""
Schemas de Cliente para validação e serialização de dados.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional


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
        from_attributes = True
