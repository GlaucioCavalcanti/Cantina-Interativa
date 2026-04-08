"""
Aplicação FastAPI - Cantina Interativa ESUDA

Módulo principal que configura as rotas, middlewares e inicializa a aplicação.
"""

from fastapi import FastAPI, HTTPException, status, Depends
from sqlalchemy.orm import Session
import uvicorn

# Importa configurações do banco de dados
from backend.app.core.database import init_db, get_db

# Importa modelos ORM
from backend.app.models import Cliente, Produto

# Importa schemas Pydantic para validação
from backend.app.schemas.cliente import ClienteCreate, ClienteUpdate, ClienteRead
from backend.app.schemas.produto import ProdutoCreate, ProdutoUpdate, ProdutoRead

# ==========================================
# INSTÂNCIA DA APLICAÇÃO
# ==========================================

app = FastAPI(
    title="Cantina Interativa ESUDA",
    description="API para gerenciar pedidos e cardápio da cantina",
    version="1.0.0"
)


# ==========================================
# EVENTO DE STARTUP
# ==========================================

@app.on_event("startup")
def startup_event():
    """Inicializa o banco de dados no startup da aplicação."""
    print("[INFO] Inicializando banco de dados...")
    init_db()
    print("[INFO] Banco de dados criado/atualizado com sucesso!")


# ==========================================
# ROTAS DE CLIENTES
# ==========================================

@app.get(
    '/clientes',
    response_model=list[ClienteRead],
    status_code=status.HTTP_200_OK,
    tags=["Clientes"],
    summary="Listar todos os clientes"
)
def listar_clientes(db: Session = Depends(get_db)):
    """
    Retorna uma lista de todos os clientes cadastrados.
    
    Returns:
        list[ClienteRead]: Lista de clientes do banco de dados
    """
    clientes = db.query(Cliente).all()
    return clientes


@app.post(
    '/clientes',
    response_model=ClienteRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Clientes"],
    summary="Criar novo cliente"
)
def criar_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    """
    Cria um novo cliente no banco de dados.
    
    Args:
        cliente: Dados do cliente (nome e email)
        db: Sessão do banco de dados injetada
        
    Returns:
        ClienteRead: Cliente criado com ID atribuído
        
    Raises:
        HTTPException: Se o email já está cadastrado
    """
    # Verifica se o email já existe
    cliente_existente = db.query(Cliente).filter(Cliente.email == cliente.email).first()
    if cliente_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado no sistema."
        )
    
    # Cria novo cliente ORM
    novo_cliente = Cliente(nome=cliente.nome, email=cliente.email)
    db.add(novo_cliente)
    db.commit()
    db.refresh(novo_cliente)
    
    return novo_cliente


@app.get(
    '/clientes/{cliente_id}',
    response_model=ClienteRead,
    status_code=status.HTTP_200_OK,
    tags=["Clientes"],
    summary="Buscar cliente por ID"
)
def buscar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """
    Busca um cliente específico pelo ID.
    
    Args:
        cliente_id: ID do cliente
        db: Sessão do banco de dados injetada
        
    Returns:
        ClienteRead: Dados do cliente
        
    Raises:
        HTTPException: Se o cliente não for encontrado
    """
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado no sistema."
        )
    return cliente


@app.put(
    '/clientes/{cliente_id}',
    response_model=ClienteRead,
    status_code=status.HTTP_200_OK,
    tags=["Clientes"],
    summary="Atualizar cliente"
)
def atualizar_cliente(
    cliente_id: int,
    cliente_update: ClienteUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualiza os dados de um cliente.
    
    Args:
        cliente_id: ID do cliente a atualizar
        cliente_update: Dados parciais a atualizar
        db: Sessão do banco de dados injetada
        
    Returns:
        ClienteRead: Cliente com dados atualizados
        
    Raises:
        HTTPException: Se o cliente não for encontrado
    """
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado no sistema."
        )
    
    # Atualiza apenas campos fornecidos
    if cliente_update.nome:
        cliente.nome = cliente_update.nome
    if cliente_update.email:
        cliente.email = cliente_update.email
    
    db.commit()
    db.refresh(cliente)
    return cliente


@app.delete(
    '/clientes/{cliente_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Clientes"],
    summary="Deletar cliente"
)
def deletar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """
    Remove um cliente do banco de dados.
    
    Args:
        cliente_id: ID do cliente a remover
        db: Sessão do banco de dados injetada
        
    Raises:
        HTTPException: Se o cliente não for encontrado
    """
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado no sistema."
        )
    
    db.delete(cliente)
    db.commit()
    return None


# ==========================================
# ROTAS DE PRODUTOS (CARDÁPIO)
# ==========================================

@app.get(
    '/produtos',
    response_model=list[ProdutoRead],
    status_code=status.HTTP_200_OK,
    tags=["Produtos"],
    summary="Listar todos os produtos"
)
def listar_produtos(db: Session = Depends(get_db)):
    """
    Retorna uma lista de todos os produtos cadastrados.
    
    Returns:
        list[ProdutoRead]: Lista de produtos do banco de dados
    """
    produtos = db.query(Produto).all()
    return produtos


@app.get(
    '/produtos/{produto_id}',
    response_model=ProdutoRead,
    status_code=status.HTTP_200_OK,
    tags=["Produtos"],
    summary="Buscar produto por ID"
)
def buscar_produto(produto_id: int, db: Session = Depends(get_db)):
    """
    Busca um produto específico pelo ID.
    
    Args:
        produto_id: ID do produto
        db: Sessão do banco de dados injetada
        
    Returns:
        ProdutoRead: Dados do produto
        
    Raises:
        HTTPException: Se o produto não for encontrado
    """
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não cadastrado no cardápio."
        )
    return produto


@app.post(
    '/produtos',
    response_model=ProdutoRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Produtos"],
    summary="Criar novo produto"
)
def criar_produto(produto: ProdutoCreate, db: Session = Depends(get_db)):
    """
    Cria um novo produto no banco de dados.
    
    Args:
        produto: Dados do produto (nome, preço e descrição)
        db: Sessão do banco de dados injetada
        
    Returns:
        ProdutoRead: Produto criado com ID atribuído
    """
    novo_produto = Produto(
        nome=produto.nome,
        preco=produto.preco,
        descricao=produto.descricao
    )
    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)
    return novo_produto


@app.put(
    '/produtos/{produto_id}',
    response_model=ProdutoRead,
    status_code=status.HTTP_200_OK,
    tags=["Produtos"],
    summary="Atualizar produto"
)
def atualizar_produto(
    produto_id: int,
    produto_update: ProdutoUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualiza os dados de um produto.
    
    Args:
        produto_id: ID do produto a atualizar
        produto_update: Dados parciais a atualizar
        db: Sessão do banco de dados injetada
        
    Returns:
        ProdutoRead: Produto com dados atualizados
        
    Raises:
        HTTPException: Se o produto não for encontrado
    """
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado no cardápio."
        )
    
    # Atualiza apenas campos fornecidos
    if produto_update.nome:
        produto.nome = produto_update.nome
    if produto_update.preco:
        produto.preco = produto_update.preco
    if produto_update.descricao:
        produto.descricao = produto_update.descricao
    
    db.commit()
    db.refresh(produto)
    return produto


@app.delete(
    '/produtos/{produto_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Produtos"],
    summary="Deletar produto"
)
def deletar_produto(produto_id: int, db: Session = Depends(get_db)):
    """
    Remove um produto do banco de dados.
    
    Args:
        produto_id: ID do produto a remover
        db: Sessão do banco de dados injetada
        
    Raises:
        HTTPException: Se o produto não for encontrado
    """
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado no cardápio."
        )
    
    db.delete(produto)
    db.commit()
    return None


# ==========================================
# ROTA DE SAÚDE (HEALTH CHECK)
# ==========================================

@app.get(
    '/health',
    status_code=status.HTTP_200_OK,
    tags=["Health"],
    summary="Verificar saúde da API"
)
def health_check():
    """
    Verifica se a aplicação está rodando corretamente.
    
    Returns:
        dict: Status da aplicação
    """
    return {"status": "ok", "message": "Cantina Interativa está rodando!"}


# ==========================================
# INICIALIZAÇÃO DO SERVIDOR ASGI
# ==========================================

if __name__ == '__main__':
    """
    Inicia o servidor Uvicorn com reload automático.
    Limita os diretórios observados para evitar recarregamentos infinitos.
    """
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=["backend"],
        reload_excludes=[".venv/*", "venv/*"],
    )