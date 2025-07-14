from fastapi import APIRouter, Depends, HTTPException
from models import Usuario
from dependencies import pegar_sessao, verificar_token
from main import bcrypt_context, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from schemas import LoginSchema, UsuarioSchema
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm

auth_router = APIRouter(prefix="/auth", tags=["Autenticação"])

def criar_token(id_usuario, duracao_token=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    data_expiracao = datetime.now(timezone.utc)+duracao_token
    dic_info = {"sub" : str(id_usuario), "exp" : data_expiracao}
    jwt_codificado = jwt.encode(dic_info, SECRET_KEY, ALGORITHM)
    return jwt_codificado

def autenticar_usuario(email, senha, session):
    usuario = session.query(Usuario).filter(Usuario.email==email).first()
    if not usuario:
       return False
    elif not bcrypt_context.verify(senha, usuario.senha):
       return False
    return usuario
     
     

@auth_router.get("/")
async def home():
    """Autenticar:  
        Verifica se está funcionado o acesso a rota de Autenticação.
    """
    return {"mensagem": "Você acessou a rota padrão de autenticação", "CODE": "200"}

@auth_router.post("/criar_conta")
async def criar_conta(usuario_schema: UsuarioSchema, session: Session = Depends(pegar_sessao)):
    """Criar conta:  
        Operação que cria uma nova conta.
        
        Recebe os dados e cria a conta.
        
        Realiza criptografia da senha(HS256). Atualiza o banco de dados.

        Recebe os dados no formato:

            {
            "nome": "string",
            "email": "string",
            "senha": "string",
            "ativo": true,
            "admin": true
            }

        ERRO 400: E-mail já cadastrado.
    """    
    usuario = session.query(Usuario).filter(Usuario.email==usuario_schema.email).first()

    if usuario:
        raise HTTPException(status_code = 400, detail = "E-mail já cadastrado.")
    else:
        senha_criptografada = bcrypt_context.hash(usuario_schema.senha)
        novo_usuario = Usuario(usuario_schema.nome, usuario_schema.email, senha_criptografada, usuario_schema.ativo, usuario_schema.admin, )
        session.add(novo_usuario)
        session.commit()
        return {"mensagem": "usuario criado com sucesso."}
        
@auth_router.post("/login")
async def login(login_schema: LoginSchema, session: Session = Depends(pegar_sessao)):
    """Login:  
        Operação que realiza login.
        
        Recebe os dados de login e faz a verificação de forma criptogafada.
        
        Cria os tokens de acesso(access_token e refresh_token) no padrão JWT.

        Após o login, o token de acesso deve ser enviado no header das próximas requisições no seguinte formato:
    
            headers = {
                "Authorization": "Bearer <access_token>"
            }
    
        Caso esteja utilizando o Swagger (FastAPI docs), você pode clicar no botão "Authorize" e fazer login que o token será enviado automaticamente.

        Recebe os dados no formato:

            {
            "email": "string",
            "senha": "string",
            }

        ERRO 400: Usuario não encontrado ou senha inválida.
    """    
    usuario = autenticar_usuario(login_schema.email, login_schema.senha, session)
    if not usuario:
        raise HTTPException(status_code = 400, detail = "Usuario não encontrado ou senha inválida")
    else:
        access_token = criar_token((usuario.id))
        refresh_token = criar_token(usuario.id, duracao_token=timedelta(days=7))
        return{
            "access_token" : access_token,
            "refresh_token" : refresh_token,
            "token_type" : "Bearer"
        }

@auth_router.post("/login-form")
async def login_form(dados_formulario: OAuth2PasswordRequestForm = Depends() , session: Session = Depends(pegar_sessao)):
    """Login form:  
        Operação que realiza login usando o formulário de login do FASTAPI.
        
        Recebe os dados de login e faz a verificação de forma criptogafada.
        
        Cria o token de acesso(access_token) no padrão JWT.

        Devolve os dados seguindo o padrão "OAuth2PasswordBearer".

        ERRO 400: Usuario não encontrado ou senha inválida.
    """ 
    usuario = autenticar_usuario(dados_formulario.username, dados_formulario.password, session)
    if not usuario:
        raise HTTPException(status_code = 400, detail = "Usuario nao encontrado ou senha inválida")
    else:
        access_token = criar_token((usuario.id))        
        return{
            "access_token" : access_token,           
            "token_type" : "Bearer"
        }
    
@auth_router.get("/refresh")
async def use_refresh_token(usuario: Usuario = Depends(verificar_token)):
    """Refresh:  
        Para realizar a operação usuário deve estar devidamente logado no sistema.
        
        Cria um novo token de acesso(access_token) no padrão JWT.

        Devolve os dados deguindo o padrão "OAuth2PasswordBearer".

        ERRO 401: Usuario não autenticado.
    """
   
    access_token = criar_token(usuario.id)
    return {
        "access_token" : access_token,
        "token_type" : "Bearer"
    }