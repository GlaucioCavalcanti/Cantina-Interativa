# Guia de Setup e Execução - Cantina Interativa ESUDA

## Visão Geral da Refatoração

A aplicação foi refatorada seguindo as melhores práticas de **Clean Code** e **Clean Architecture**:

### Principais Melhorias

✅ **Banco de Dados Integrado**: Migrado de dicionários em memória para SQLAlchemy + SQLite  
✅ **Separação de Conceitos**: Modelos ORM separados dos Schemas Pydantic  
✅ **Estrutura Modularizada**: Cada modelo em seu próprio arquivo  
✅ **Dependency Injection**: Use de `get_db` para injetar sessões  
✅ **Documentação Automática**: Swagger UI integrado no FastAPI  
✅ **Tratamento de Erros**: Validações e exceções HTTP padronizadas  

---

## 📁 Nova Estrutura de Diretórios

```
backend/
│
├── main.py                          # Arquivo principal (rotas e startup)
│
├── app/
│   ├── __init__.py
│   │
│   ├── core/                        # Configurações centrais
│   │   ├── __init__.py
│   │   └── database.py              # SessionLocal, Base, get_db()
│   │
│   ├── models/                      # Modelos ORM (SQLAlchemy)
│   │   ├── __init__.py              # Importações dos modelos
│   │   ├── models.py                # Re-exports dos modelos
│   │   ├── cliente.py               # Modelo ORM Cliente
│   │   └── produto.py               # Modelo ORM Produto
│   │
│   ├── schemas/                     # Modelos de Validação (Pydantic)
│   │   ├── __init__.py              # Importações centralizadas
│   │   ├── cliente.py               # Schemas: ClienteCreate, ClienteRead, etc
│   │   └── produto.py               # Schemas: ProdutoCreate, ProdutoRead, etc
│   │
│   ├── routes/                      # (Futuro) Separar rotas em módulos
│   │   ├── __init__.py
│   │   ├── clientes.py              # Rotas relacionadas a clientes
│   │   └── produtos.py              # Rotas relacionadas a produtos
│   │
│   ├── utils/                       # Funções utilitárias
│   └── views/                       # (Se usar templates)
│
└── tests/                           # (Futuro) Testes automatizados
    └── __init__.py
```

---

## 🚀 Como Executar o Projeto

### Pré-requisitos

- **Python 3.9+** instalado
- **pip** (gestor de pacotes Python)
- Terminal/PowerShell aberto no diretório do projeto

### 1️⃣ Ativar o Ambiente Virtual

Se ainda não tem ambiente virtual, crie um:

```bash
# Windows
python -m venv .venv
.venv\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 2️⃣ Instalar Dependências

```bash
pip install -r requirements.txt
```

**Pacotes instalados:**
- `fastapi==0.104.1` - Framework web
- `uvicorn[standard]==0.24.0` - Servidor ASGI
- `pydantic==2.5.0` - Validação de dados
- `sqlalchemy==2.0.23` - ORM e acesso a banco de dados
- `alembic==1.12.1` - Migrações de banco de dados
- `python-dotenv==1.0.0` - Gerenciamento de variáveis de ambiente

### 3️⃣ Executar a Aplicação

```bash
# Opção 1: Executar direto (com reload automático)
python backend\main.py

# Opção 2: Usar uvicorn diretamente
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### 4️⃣ Acessar a Aplicação

Abra seu navegador e acesse:

- **API Principal**: http://127.0.0.1:8000
- **Documentação Swagger**: http://127.0.0.1:8000/docs
- **Documentação ReDoc**: http://127.0.0.1:8000/redoc
- **Health Check**: http://127.0.0.1:8000/health

---

## 📊 Banco de Dados

### Tipo: SQLite (Padrão)

O banco de dados é criado automaticamente no startup:

- **Arquivo**: `database.db` (na raiz do projeto)
- **Criação automática**: Tabelas são criadas pela função `init_db()`
- **Desenvolvimento**: Perfeito para testes e prototipagem

### Alternar para PostgreSQL (Produção)

Se quiser usar PostgreSQL:

1. Instale o driver:
```bash
pip install psycopg2-binary
```

2. Atualize `backend/app/core/database.py`:
```python
DATABASE_URL = "postgresql://usuario:senha@localhost:5432/cantina_db"
```

3. Remova as configurações SQLite:
```python
# Remova: connect_args={"check_same_thread": False}
```

---

## 🔄 Fluxo de Dependency Injection

Como o banco de dados é injetado automaticamente nas rotas:

```python
from fastapi import Depends
from backend.app.core.database import get_db

@app.get('/clientes')
def listar_clientes(db: Session = Depends(get_db)):
    # db é uma sessão ativa
    clientes = db.query(Cliente).all()
    return clientes
```

**O que acontece:**
1. FastAPI vê `Depends(get_db)` no parâmetro `db`
2. Chama a função `get_db()` antes de executar a rota
3. Garante que a sessão seja fechada depois (`finally` no get_db)
4. Impede vazamento de recursos (memory leaks)

---

## 📝 Exemplos de Requests (cURL)

### Criar Cliente

```bash
curl -X POST "http://127.0.0.1:8000/clientes" \
  -H "Content-Type: application/json" \
  -d '{"nome": "João Silva", "email": "joao@example.com"}'
```

### Listar Clientes

```bash
curl -X GET "http://127.0.0.1:8000/clientes"
```

### Buscar Cliente por ID

```bash
curl -X GET "http://127.0.0.1:8000/clientes/1"
```

### Atualizar Cliente

```bash
curl -X PUT "http://127.0.0.1:8000/clientes/1" \
  -H "Content-Type: application/json" \
  -d '{"nome": "João Silva Atualizado"}'
```

### Deletar Cliente

```bash
curl -X DELETE "http://127.0.0.1:8000/clientes/1"
```

### Criar Produto

```bash
curl -X POST "http://127.0.0.1:8000/produtos" \
  -H "Content-Type: application/json" \
  -d '{"nome": "Hambúrguer", "preco": 35.50, "descricao": "Pão, carne, alface, tomate"}'
```

---

## 🔄 Migrações com Alembic (Futuro)

Para versionar as alterações no banco de dados no futuro:

```bash
# Inicializar Alembic
alembic init migrations

# Criar migração automática
alembic revision --autogenerate -m "Adicionar tabela de pedidos"

# Aplicar migrações
alembic upgrade head
```

Por enquanto, o `init_db()` cuida de criar as tabelas automaticamente.

---

## 🛡️ Variáveis de Ambiente (.env)

Se quiser adicionar configurações sensíveis, crie um arquivo `.env`:

```env
DATABASE_URL=sqlite:///./database.db
DEBUG=True
SECRET_KEY=sua_chave_secreta_aqui
```

Depois carregue com:

```python
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")
```

---

## 🔍 Resolvendo Erros Comuns

### Erro: "ModuleNotFoundError: No module named 'backend'"

**Solução**: Certifique-se de executar o projeto da raiz:
```bash
# ✅ Correto
python backend\main.py

# ❌ Errado
cd backend && python main.py
```

### Erro: "sqlite3.OperationalError: unable to open database file"

**Solução**: Verificar permissões de escrita no diretório.

### Erro: "Email já cadastrado"

**Solução**: O banco agora valida emails únicos. Use um email diferente.

---

## 📚 Próximos Passos (Recomendações)

1. **Separar rotas por módulo**: Mover rotas para `backend/app/routes/`
2. **Adicionar testes**: Usar `pytest` para testes automatizados
3. **Autenticação**: Implementar JWT para segurança
4. **Logging**: Configurar logs estruturados
5. **CORS**: Se frontend estiver em outro domínio
6. **Validações extras**: CPF, telefone, validações de negócio
7. **Paginação**: Adicionar limit/offset nas listagens

---

## 📞 Suporte

Se tiver dúvidas sobre a estrutura ou implementação, consulte:

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Pydantic Docs](https://docs.pydantic.dev/)

---

**Bem-vindo ao Backend Refatorado! 🎉**
