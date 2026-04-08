# Arquitetura e Conceitos - Cantina Interativa

## 🏗️ Arquitetura da Aplicação

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENTE HTTP (Browser/cURL)              │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    FASTAPI ROUTER (main.py)                 │
│  ┌──────────────────────┐  ┌──────────────────────────────┐ │
│  │  GET /clientes       │  │  POST /clientes   (req/resp) │ │
│  │  PUT /clientes/{id}  │  │  DELETE /clientes/{id}       │ │
│  │  GET /produtos       │  │  GET/POST/PUT/DELETE /...    │ │
│  └──────────────────────┘  └──────────────────────────────┘ │
└──────────────────────────────┬──────────────────────────────┘
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
    ┌──────────────────────┐      ┌──────────────────────┐
    │   SCHEMA VALIDATION  │      │  DEPENDENCY INJECT   │
    │   (Pydantic)         │      │   (get_db function)  │
    │                      │      │                      │
    │ ClienteCreate        │      │ def get_db()         │
    │ ClienteRead          │      │   → SessionLocal()   │
    │ ProdutoCreate        │      │   → yield db         │
    │ ProdutoRead          │      │   → db.close()       │
    └──────────────────────┘      └──────────────────────┘
                │                             │
                └──────────────┬──────────────┘
                               ▼
      ┌────────────────────────────────────────────────┐
      │         SQLALCHEMY ORM MODELS                  │
      │  ┌───────────────────────────────────────────┐ │
      │  │  class Cliente(Base)                      │ │
      │  │      __tablename__ = "clientes"           │ │
      │  │      id = Column(Integer, primary_key)    │ │
      │  │      nome = Column(String(150))           │ │
      │  │      email = Column(String, unique)       │ │
      │  └───────────────────────────────────────────┘ │
      │  ┌───────────────────────────────────────────┐ │
      │  │  class Produto(Base)                      │ │
      │  │      __tablename__ = "produtos"           │ │
      │  │      id = Column(Integer, primary_key)    │ │
      │  │      nome = Column(String(200))           │ │
      │  │      preco = Column(Float)                │ │
      │  │      descricao = Column(String(500))      │ │
      │  └───────────────────────────────────────────┘ │
      └────────────────────────────────────────────────┘
                               ▼
      ┌────────────────────────────────────────────────┐
      │  SQLALCHEMY ENGINE & SESSION FACTORY           │
      │                                                │
      │  create_engine("sqlite:///./database.db")      │
      │  SessionLocal = sessionmaker(bind=engine)      │
      │  Base = declarative_base()                     │
      └────────────────────────────────────────────────┘
                               ▼
      ┌────────────────────────────────────────────────┐
      │           DATABASE (SQLite)                    │
      │                                                │
      │  ┌─────────────────────────────────────────┐   │
      │  │  TABLE: clientes                        │   │
      │  │  ├─ id (INTEGER, PK)                    │   │
      │  │  ├─ nome (VARCHAR(150))                 │   │
      │  │  └─ email (VARCHAR(255), UNIQUE)        │   │
      │  └─────────────────────────────────────────┘   │
      │  ┌─────────────────────────────────────────┐   │
      │  │  TABLE: produtos                        │   │
      │  │  ├─ id (INTEGER, PK)                    │   │
      │  │  ├─ nome (VARCHAR(200))                 │   │
      │  │  ├─ preco (FLOAT)                       │   │
      │  │  └─ descricao (VARCHAR(500))            │   │
      │  └─────────────────────────────────────────┘   │
      └────────────────────────────────────────────────┘
```

---

## 🔑 Conceitos-Chave

### 1. **Separação Pydantic vs SQLAlchemy**

| Aspecto | Pydantic (Schemas) | SQLAlchemy (Models) |
|--------|------------------|------------------|
| **Propósito** | Validar dados HTTP | Mapeamento de tabelas |
| **Quando usar** | Request/Response | Operações BD |
| **Exemplo** | `ClienteCreate` | `Cliente` |
| **Benefício** | Flexibilidade de API | Flexibilidade de BD |

```python
# Schema Pydantic - Validação HTTP
class ClienteCreate(BaseModel):
    nome: str
    email: EmailStr

# Model ORM - Tabela no BD
class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True)
    nome = Column(String(150))
    email = Column(String(255), unique=True)
```

### 2. **Dependency Injection com FastAPI**

O padrão `Depends(get_db)` garante:

✅ **Sessão por requisição**: Cada rota recebe sua própria sessão  
✅ **Limpeza automática**: A sessão é fechada após a rota terminar  
✅ **Segurança**: Evita conexões abertas (memory leak)  
✅ **Testabilidade**: Fácil mockar o `get_db` em testes  

```python
# Antes (Ruim)
@app.get('/clientes')
def listar():
    db = SessionLocal()  # Pode esquecer de fechar
    clientes = db.query(Cliente).all()
    # Esqueceu db.close() → LEAK!
    return clientes

# Depois (Bom)
@app.get('/clientes')
def listar(db: Session = Depends(get_db)):
    clientes = db.query(Cliente).all()
    # get_db cuida de fechar automaticamente
    return clientes
```

### 3. **Status HTTP Corretos**

| Status | Significado | Quando Usar |
|--------|-----------|-----------|
| `200 OK` | Sucesso em GET | Listar, Buscar |
| `201 Created` | Recurso criado | POST bem-sucedido |
| `204 No Content` | Sucesso sem corpo | DELETE bem-sucedido |
| `400 Bad Request` | Email duplicado | Validação falhou |
| `404 Not Found` | ID não existe | Recurso não encontrado |
| `500 Internal Error` | Erro no servidor | Exception não tratada |

### 4. **Validação Automática com Pydantic**

```python
# Request inválida:
POST /clientes
{
    "nome": "João",
    "email": "invalid-email"  # ❌ EmailStr rejeita
}

# Resposta automática:
{
    "detail": [
        {
            "type": "value_error",
            "loc": ["body", "email"],
            "msg": "invalid email format"
        }
    ]
}
```

### 5. **Resource Management com Context Manager**

```python
def get_db():
    db = SessionLocal()
    try:
        yield db  # Enquanto a rota executa
    finally:
        db.close()  # SEMPRE executa, mesmo se erro
```

---

## 📊 Fluxo de Criação de Cliente

```
1. Cliente HTTP envia:
   POST /clientes
   {"nome": "João", "email": "joao@example.com"}

2. FastAPI recebe e valida com Pydantic:
   ClienteCreate(nome="João", email="joao@example.com")

3. Dependency Injection fornece db:
   db = SessionLocal()

4. Rota executa lógica de negócio:
   cliente_existente = db.query(Cliente).filter(...).first()
   if cliente_existente: raise HTTPException(...)

5. Cria modelo ORM:
   novo_cliente = Cliente(nome="João", email="joao@example.com")

6. Persiste no banco:
   db.add(novo_cliente)
   db.commit()
   db.refresh(novo_cliente)

7. Converte para schema de resposta:
   return novo_cliente  # ClienteRead serializa automaticamente

8. FastAPI retorna JSON:
   {
       "id": 1,
       "nome": "João",
       "email": "joao@example.com"
   }

9. Dependency injection finaliza:
   db.close()  # Sessão fechada (no finally de get_db)
```

---

## 🛡️ Tratamento de Erros

### Padrão de Erro Consistente

```python
# ❌ Ruim
@app.delete('/clientes/{id}')
def deletar(id: int):
    # Pode gerar erro genérico SQL
    db.query(Cliente).filter(id == id).delete()

# ✅ Bom
@app.delete('/clientes/{id}')
def deletar(id: int, db = Depends(get_db)):
    cliente = db.query(Cliente).filter(...).first()
    if not cliente:
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado"
        )
    db.delete(cliente)
    db.commit()
```

### Resposta de Erro

```json
{
    "detail": "Cliente não encontrado"
}
```

---

## 🔄 Clean Code Principles Aplicados

| Princípio | Implementação |
|-----------|--------------|
| **SRP** | Cada arquivo tem responsabilidade única |
| **DRY** | Schemas compartilhados, modelos centralizados |
| **SOLID** | Dependency Injection, models separados |
| **Testability** | get_db pode ser mockado facilmente |
| **Readability** | Nomes descritivos, type hints, docstrings |

---

## 🚀 Escalabilidade Futura

```
Backend modularizado permite:

├── Adicionar autenticação (JWT)
│   └── backend/app/core/security.py
│
├── Adicionar cache (Redis)
│   └── backend/app/core/cache.py
│
├── Adicionar logging estruturado
│   └── backend/app/core/logging.py
│
├── Separar rotas em blueprints
│   ├── backend/app/routes/clientes.py
│   ├── backend/app/routes/produtos.py
│   └── backend/app/routes/pedidos.py
│
├── Adicionar services/use cases
│   ├── backend/app/services/cliente_service.py
│   └── backend/app/services/produto_service.py
│
└── Adicionar testes
    ├── tests/test_clientes.py
    ├── tests/test_produtos.py
    └── tests/conftest.py (fixtures)
```

---

## 📚 Recursos Adicionais

- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/orm/)
- [Clean Code by Robert C. Martin](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882)
- [Design Patterns in Python](https://refactoring.guru/design-patterns/python)

---

**Estrutura implementada com excelência técnica! 🎯**
