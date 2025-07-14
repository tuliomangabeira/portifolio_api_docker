# Delivery ou Site de Pedidos

## Versão Docker
- Foi adicionado ao projeto original os arquivos e configurações para criação de imagens Docker, e também o github actions.
- Baixe todos os arquivos
- Com o Docker instalado e inicializado, execute o seguinte comando no terminal.
    ```sh
   docker compose up
   ```
- Será criado e inicializado o container da aplicação.
- Acesse usando a mesma rota do FASTAPI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)


Este projeto é uma API desenvolvida com FastAPI para integrar sistemas com pedidos e que exijam cadastro e autenticação.
- Criação de novos usuários no banco de dados, seguindo padrão de criptografia de senha HS256, e geração de token JWT.
- Operações somente para usuários autenticados, e outras específicas de usuário ADMIN.
- Manipulação dos pedidos(Criação, inclusão/exclussão de itens, alteração de status, e consulta dos dados armazenados).

---

## Passos para testar o projeto

1. **Instale as dependências:**
    Com o ambiente virtual já criado e ativo:

   ```sh
   pip install -r requirements.txt
   ```

2. **Para correto funcionamento do teste:** 
    - crie um arquivo .env e inclua os dados: "SECRET_KEY = QnDjPlQ0ZdRtzvbXwvzfDieNi5TqDXAT", "ALGORITHM = HS256", "ACCESS_TOKEN_EXPIRE_MINUTES = 30"
    - para teste utilize como login: "username: teste@admin.com, password: 123456" --- para requisições de ADMIN, "username: teste@gmail.com, password: 123456" --- para requisições normais(utilizando o banco de dados de testes "banco.db")

3. **Execute a aplicação:**
   ```sh
   uvicorn main:app --reload
   ```

4. **Acesse a documentação interativa:**

   Abra o navegador e acesse:  
   [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

   Aqui você pode testar todos os endpoints da API de forma interativa.

---

## Estrutura do Projeto

- `main.py`: Arquivo principal da aplicação FastAPI.
- `models.py`: Modelos do banco de dados (SQLAlchemy).
- `schemas.py`: Schemas de validação (Pydantic).
- `order_routes`: Rotas de pedidos.
- `auth_routes`: Rotas de autenticação.
- `requirements.txt`: Lista de dependências do projeto.

---

