"""Pacote de modelos de dados (Pydantic) para a aplicação.

Adicionar este arquivo torna `app.models` um pacote Python completo, permitindo
importações explícitas como:

    from app.models import Cliente, Produto

"""

from .models import Cliente, Produto

__all__ = ["Cliente", "Produto"]
