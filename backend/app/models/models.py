"""
Modelos ORM da aplicação.

Este módulo centraliza as importações dos modelos ORM para facilitar
importações em toda a aplicação.

Exemplo:
    from backend.app.models import Cliente, Produto
"""

from backend.app.models.cliente import Cliente
from backend.app.models.produto import Produto

__all__ = ["Cliente", "Produto"]
