"""
Exemplo de teste com FastAPI TestClient - Demonstração

Este arquivo mostra como testar rotas da aplicação usando pytest e TestClient.
Para usar, instale: pip install pytest pytest-asyncio

Como rodar os testes:
    pytest tests/test_exemplo.py -v
"""

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

# Importa a aplicação e dependências
from backend.main import app
from backend.app.core.database import Base, get_db
from backend.app.models import Cliente, Produto

# ==========================================
# CONFIGURAÇÃO DE BD PARA TESTES
# ==========================================

# Usa BD em memória para testes (não modifica database.db)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    """Função que substitui get_db durante testes."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Substitui a função original pela de teste
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# ==========================================
# TESTES DAS ROTAS DE CLIENTES
# ==========================================

@pytest.fixture(autouse=True)
def reset_database():
    """Limpa a BD antes de cada teste."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_criar_cliente():
    """Testa criação de cliente."""
    response = client.post(
        "/clientes",
        json={"nome": "João Silva", "email": "joao@example.com"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == "João Silva"
    assert data["email"] == "joao@example.com"
    assert data["id"] is not None


def test_criar_cliente_email_duplicado():
    """Testa que não permite email duplicado."""
    # Cria primeiro cliente
    client.post(
        "/clientes",
        json={"nome": "João", "email": "joao@example.com"}
    )
    
    # Tenta criar com mesmo email
    response = client.post(
        "/clientes",
        json={"nome": "João 2", "email": "joao@example.com"}
    )
    assert response.status_code == 400
    assert "Email já cadastrado" in response.json()["detail"]


def test_criar_cliente_email_invalido():
    """Testa validação de email inválido."""
    response = client.post(
        "/clientes",
        json={"nome": "João", "email": "email-invalido"}
    )
    assert response.status_code == 422  # Unprocessable Entity


def test_listar_clientes_vazio():
    """Testa listagem quando não há clientes."""
    response = client.get("/clientes")
    assert response.status_code == 200
    assert response.json() == []


def test_listar_clientes_com_dados():
    """Testa listagem com clientes cadastrados."""
    # Cria dois clientes
    client.post(
        "/clientes",
        json={"nome": "João", "email": "joao@example.com"}
    )
    client.post(
        "/clientes",
        json={"nome": "Maria", "email": "maria@example.com"}
    )
    
    response = client.get("/clientes")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_buscar_cliente_por_id():
    """Testa busca de cliente específico."""
    # Cria cliente
    criar = client.post(
        "/clientes",
        json={"nome": "João", "email": "joao@example.com"}
    )
    cliente_id = criar.json()["id"]
    
    # Busca por ID
    response = client.get(f"/clientes/{cliente_id}")
    assert response.status_code == 200
    assert response.json()["nome"] == "João"


def test_buscar_cliente_inexistente():
    """Testa busca de cliente que não existe."""
    response = client.get("/clientes/999")
    assert response.status_code == 404
    assert "Cliente não encontrado" in response.json()["detail"]


def test_atualizar_cliente():
    """Testa atualização de cliente."""
    # Cria cliente
    criar = client.post(
        "/clientes",
        json={"nome": "João", "email": "joao@example.com"}
    )
    cliente_id = criar.json()["id"]
    
    # Atualiza
    response = client.put(
        f"/clientes/{cliente_id}",
        json={"nome": "João Silva"}
    )
    assert response.status_code == 200
    assert response.json()["nome"] == "João Silva"


def test_deletar_cliente():
    """Testa deleção de cliente."""
    # Cria cliente
    criar = client.post(
        "/clientes",
        json={"nome": "João", "email": "joao@example.com"}
    )
    cliente_id = criar.json()["id"]
    
    # Deleta
    response = client.delete(f"/clientes/{cliente_id}")
    assert response.status_code == 204
    
    # Verifica que foi deletado
    response_get = client.get(f"/clientes/{cliente_id}")
    assert response_get.status_code == 404


# ==========================================
# TESTES DAS ROTAS DE PRODUTOS
# ==========================================

def test_criar_produto():
    """Testa criação de produto."""
    response = client.post(
        "/produtos",
        json={
            "nome": "Hambúrguer",
            "preco": 35.50,
            "descricao": "Pão, carne, alface, tomate"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == "Hambúrguer"
    assert data["preco"] == 35.50


def test_listar_produtos():
    """Testa listagem de produtos."""
    # Cria alguns produtos
    client.post(
        "/produtos",
        json={"nome": "Hambúrguer", "preco": 35.50, "descricao": "Desc 1"}
    )
    client.post(
        "/produtos",
        json={"nome": "Refrigerante", "preco": 8.50, "descricao": "Desc 2"}
    )
    
    response = client.get("/produtos")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_health_check():
    """Testa se a API está saudável."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# ==========================================
# COMO EXECUTAR OS TESTES
# ==========================================

"""
Comando para rodar todos os testes:
    pytest tests/ -v

Comando para rodar um teste específico:
    pytest tests/test_exemplo.py::test_criar_cliente -v

Comando com cobertura de código:
    pip install pytest-cov
    pytest tests/ --cov=backend --cov-report=html

Comando para rodar com output detalhado:
    pytest tests/ -vv -s
"""

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
