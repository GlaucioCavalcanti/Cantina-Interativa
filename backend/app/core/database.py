"""
Módulo de configuração do banco de dados.

Este módulo gerencia a conexão com o banco de dados, criação de sessões
e disponibiliza a classe Base para os modelos ORM.

Suporta:
- SQLite (padrão para desenvolvimento)
- PostgreSQL (configurável)
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import Generator
import os

# ==========================================
# CONFIGURAÇÃO DO BANCO DE DADOS
# ==========================================

# Definir qual banco de dados usar
# Para SQLite (padrão - development): database.db será criado na pasta do projeto
# Para PostgreSQL: Descomentar e ajustar a URL conforme sua configuração
DATABASE_URL = "sqlite:///./database.db"

# DATABASE_URL = "postgresql://usuario:senha@localhost/cantina_db"
# Exemplo: "postgresql://admin:password123@localhost:5432/cantina_interativa"

# ==========================================
# ENGINE E SESSION FACTORY
# ==========================================

# Criar a engine de conexão
# Para SQLite: check_same_thread=False permite múltiplas threads (necessário para FastAPI)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=True  # Ativa logs SQL (desativar em produção)
)

# Criar a factory de sessões
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para todos os modelos ORM
Base = declarative_base()


# ==========================================
# FUNÇÃO DE DEPENDENCY INJECTION
# ==========================================

def get_db() -> Generator:
    """
    Função de dependência para injetar a sessão de banco de dados nas rotas.
    
    Yields:
        Session: Sessão ativa do banco de dados
        
    Exemplo de uso em uma rota:
        @app.get("/clientes")
        def listar_clientes(db: Session = Depends(get_db)):
            return db.query(Cliente).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================================
# FUNÇÃO DE INICIALIZAÇÃO
# ==========================================

def init_db():
    """
    Cria todas as tabelas no banco de dados.
    Execute esta função após definir todos os modelos ORM.
    
    Exemplo:
        from backend.app.core.database import init_db
        init_db()  # Deve ser chamado no startup da aplicação
    """
    Base.metadata.create_all(bind=engine)
