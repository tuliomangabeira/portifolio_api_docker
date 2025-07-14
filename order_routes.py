from fastapi import APIRouter, Depends, HTTPException
from schemas import PedidoSchema, ItemPedidoSchema
from models import Pedido, Usuario, ItemPedido
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token

order_router = APIRouter(prefix="/pedidos", tags=["pedidos"], dependencies=[Depends(verificar_token)])

@order_router.get("/")
async def pedido():
    """Pedido:  
        Operação que somente pode ser executada por usuários devidamente autenticados por meio de login efetuado. 

        Verifica se está funcionado o acesso a rota de PEDIDOS.

        ERRO 401: Usuário não autenticado.
    """

    "Rota de Pedidos"
    return {"Rota  acessada com sucesso"}

@order_router.post("/pedido-admin")
async def criar_pedido_admin(pedido_schema: PedidoSchema, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    """Criar pedido ADMIN:  
        Operação que somente pode ser executada por usuário ADMIN devidamente autenticado por meio de login efetuado. 

        Recebe um ID de um Usuário. Cria um pedido e atualiza o banco de dados.

        Recebe os dados no formato:

            {
            "usuario": 0
            }

        ERRO 401: Usuário não autenticado.
    """
    if not usuario.admin:
        raise HTTPException(status_code = 401, detail = "você não tem autorização para criar esse pedido!")
    
    usuario_alvo = session.query(Usuario).filter(Usuario.id == pedido_schema.usuario).first()
    if not usuario_alvo:
        raise HTTPException(status_code = 400, detail = "Usuário não encontrado!")
    novo_pedido = Pedido(usuario=pedido_schema.usuario)
    session.add(novo_pedido)
    session.commit()
    return {"Mensagem: " f"Pedido criado com sucesso! ID Pedido: {novo_pedido.id} "}

@order_router.post("/pedido")
async def criar_pedido_usuario(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    """Criar pedido usuário:  
        Operação que somente pode ser executada por usuários devidamente autenticados por meio de login efetuado. 

        Recebe o ID do usuário apartir do login. Cria um pedido e atualiza o banco de dados.

        ERRO 401: Usuário não autenticado.
    """
    novo_pedido = Pedido(usuario.id)
    session.add(novo_pedido)
    session.commit()
    return {"Mensagem: " f"Pedido criado com sucesso! ID Pedido: {novo_pedido.id} "}

@order_router.post("/pedido/cancelar/{id_pedido}")
async def cancelar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    """Cancelar pedido:  
        Operação que somente pode ser executada (por usuário ADMIN ou pelo próprio dono do pedido) devidamente autenticados por meio de login efetuado. 

        Recebe um ID do pedido. Atualiza seu status para CANCELADO e atualiza o banco de dados.

        ERRO 400: Pedido não encontrado.

        ERRO 401: Usuário não é ADMIN, ou Usuário não autenticado.
    """
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()

    if not pedido:
        raise HTTPException(status_code = 400, detail = "Pedido não encontrado!")
    if pedido.status == "CANCELADO":
        raise HTTPException(status_code = 400, detail = "Pedido já CANCELADO anteriormente!")
    if pedido.status == "CONCLUIDO":
        raise HTTPException(status_code = 400, detail = "Pedido CONCLUIDO!")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code = 401, detail = "Você não tem autorização para cancelar esse pedido!")
    
    pedido.status = "CANCELADO"
    session.commit()
    return {
        "mensagem" : f"Pedido {pedido.id} CANCELADO com sucesso,",
        "pedido" : pedido
    }

@order_router.get("/listar")
async def listar(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    """Listar pedidos:  
        Operação que somente pode ser executada por usuário ADMIN devidamente autenticado por meio de login efetuado. 

        Realiza uma busca no banco de dados e retorna uma lista com todos os pedidos armazenados.

        ERRO 401: Usuário não é ADMIN, ou Usuário não autenticado.
    """
    if not usuario.admin:
        raise HTTPException(status_code = 401, detail = "Você não tem autorização para fazer essa solicição!")
    else:
        pedido = session.query(Pedido).all()
    return {
        "pedidos" : pedido
    }

@order_router.post("/pedido/adicionar-item/{id_pedido}")
async def adicionar_item_pedido(id_pedido: int, item_pedido_schema: ItemPedidoSchema, session: Session = Depends(pegar_sessao),
                                 usuario: Usuario = Depends(verificar_token)):
    """Adicionar item pedido:  
        Operação que somente pode ser executada (por usuário ADMIN ou pelo próprio dono do pedido) devidamente autenticados por meio de login efetuado. 

        Recebe um ID do pedido.

        Recebe os itens para serem adicionados no formato:

            {
            "sabor": "string",
            "quantidade": 0,
            "tamanho": "string",
            "preco_unitario": 0
            }

        Adiciona os itens no pedido, atualiza o valor e atualiza o banco de dados.

        ERRO 400: Pedido não encontrado.

        ERRO 401: Usuário não é ADMIN, ou Usuário não autenticado. 
    """
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()

    if not pedido:
        raise HTTPException(status_code = 400, detail = "Pedido não encontrado!")
    if pedido.status == "CANCELADO":
        raise HTTPException(status_code = 400, detail = "Pedido CANCELADO!")
    if pedido.status == "CONCLUIDO":
        raise HTTPException(status_code = 400, detail = "Pedido CONCLUIDO!")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code = 401, detail = "Você não tem autorização para fazer essa operação.")
    
    item_pedido = ItemPedido(item_pedido_schema.sabor, item_pedido_schema.quantidade, item_pedido_schema.tamanho,
                                         item_pedido_schema.preco_unitario, id_pedido)
    session.add(item_pedido)
    pedido.calcular_preco()
    session.commit()
    return {
        "mensagem": "Item criado com sucesso.",
        "item_id": item_pedido.id,
        "preco_pedido": pedido.preco
    }

@order_router.post("/pedido/remover-item/{id_item_pedido}")
async def remover_item_pedido(id_item_pedido: int, session: Session = Depends(pegar_sessao),
                                 usuario: Usuario = Depends(verificar_token)):
    """Remover item pedido:  
        Operação que somente pode ser executada (por usuário ADMIN ou pelo próprio dono do pedido) devidamente autenticados por meio de login efetuado. 

        Recebe um ID de um item a ser removido do pedido.

        Procura o pedido associado a esse "item". Remove o "item" do pedido. Atualiza o valor do pedido e atualiza o banco de dados.

        ERRO 400: Pedido não encontrado.

        ERRO 401: Usuário não é ADMIN, ou Usuário não autenticado.
    """ 
    item_pedido = session.query(ItemPedido).filter(ItemPedido.id == id_item_pedido).first()

    if not item_pedido:
        raise HTTPException(status_code = 400, detail = "Pedido não encontrado para esse item!")
    
    pedido = session.query(Pedido).filter(Pedido.id == item_pedido.pedido).first()

    if pedido.status == "CANCELADO":
        raise HTTPException(status_code = 400, detail = "Pedido CANCELADO!")
    if pedido.status == "CONCLUIDO":
        raise HTTPException(status_code = 400, detail = "Pedido CONCLUIDO!")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code = 401, detail = "Você não tem autorização para fazer essa operação.")    
    
    session.delete(item_pedido)
    pedido.calcular_preco()
    session.commit()
    return {
        "mensagem": "Item removido com sucesso.",
        "quantidade_itens_pedido": len(pedido.itens),
        "pedido": pedido
    }

@order_router.post("/pedido/finalizar/{id_pedido}")
async def finalizar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    """Finalizar pedido:  
        Operação que somente pode ser executada por usuário ADMIN devidamente autenticados por meio de login efetuado. 

        Recebe um ID do pedido. Atualiza seu status para CONCLUIDO e atualiza o banco de dados.

        ERRO 400: Pedido não encontrado.

        ERRO 401: Usuário não é ADMIN, ou Usuário não autenticado.
    """
    
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()

    if not pedido:
        raise HTTPException(status_code = 400, detail = "Pedido não encontrado!")
    if pedido.status == "CANCELADO":
        raise HTTPException(status_code = 400, detail = "Pedido CANCELADO!")
    if pedido.status == "CONCLUIDO":
        raise HTTPException(status_code = 400, detail = "Pedido já estava CONCLUIDO anteriormente!")
    if not usuario.admin:
        raise HTTPException(status_code = 401, detail = "Você não tem autorização para fazer essa operação!")
    
    pedido.status = "CONCLUIDO"
    session.commit()
    return {
        "mensagem" : f"Pedido {pedido.id} CONCLUIDO com sucesso.",
        "pedido" : pedido
    }

@order_router.get("/pedido/{id_pedido}")
async def visualizar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    """Visualizar pedido:  
        Operação que somente pode ser executada por usuário ADMIN devidamente autenticados por meio de login efetuado.

        Recebe como entrada o ID de um pedido. 

        Realiza uma busca no banco de dados e retorna os dados do pedido solicitado.

        ERRO 400: Pedido não encontrado.

        ERRO 401: Usuário não é ADMIN, ou Usuário não autenticado.
    """
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()

    if not pedido:
        raise HTTPException(status_code = 400, detail = "Pedido não encontrado!")
    if not usuario.admin:
        raise HTTPException(status_code = 401, detail = "Você não tem autorização para fazer essa modificação.")
    
    return {
        "quantidade_itens_pedidos" : len(pedido.itens),
        "pedido" : pedido
    }
    
@order_router.get("/listar/pedido-usuario")
async def listar_pedido_usuario(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    """Listar pedido Usuário:  
        Operação pode ser executada por qualquer usuário devidamente autenticado por meio de login.

        Identifica o usuário logado pelo token JWT e busca no banco todos os pedidos relacionados ao seu ID. 

        ERRO 401: Usuário não autenticado.
    """
    pedidos = session.query(Pedido).filter(Pedido.usuario == usuario.id).all()
    return {
        "pedidos" : pedidos
    }