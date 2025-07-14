from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

db = create_engine("sqlite:///banco.db")

Base = declarative_base()

class Usuario(Base):
    __tablename__="usuarios"

    id = Column("id", Integer, primary_key = True, autoincrement = True)
    nome = Column("nome", String)
    email = Column("email", String, nullable = False)
    senha = Column("senha", String)
    ativo = Column("ativo", Boolean)
    admin = Column("admin", Boolean, default = False)

    def __init__(self, nome, email, senha, ativo=True, admin=False):
        self.nome = nome
        self.email= email
        self.senha = senha
        self.ativo = ativo
        self.admin = admin

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column("id", Integer, autoincrement = True, primary_key = True)
    status = Column("status", String)
    usuario = Column("usuario", ForeignKey("usuarios.id"))
    preco = Column("preco", Float)
    itens = relationship("ItemPedido", cascade = "all, delete")

    def __init__(self, usuario, status="PENDENTE", preco=0):
        self.status = status
        self.usuario = usuario
        self.preco = preco

    def calcular_preco(self):
        preco_pedido = 0
        for item in self.itens:
            preco_item = item.preco_unitario * item.quantidade
            preco_pedido += preco_item
        self.preco = preco_pedido

class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    sabor = Column("sabor", String)
    quantidade = Column("quantidade", Integer)
    tamanho = Column("tamanho", String)
    preco_unitario = Column("preco_unitario", Float)
    pedido = Column("pedido", ForeignKey("pedidos.id"))

    def __init__(self, sabor, quantidade, tamanho, preco_unitario, pedido):
        self.sabor = sabor
        self.quantidade = quantidade
        self.tamanho = tamanho
        self.preco_unitario = preco_unitario
        self.pedido = pedido