from fastapi import FastAPI
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
from fastapi.security import OAuth2PasswordBearer

load_dotenv()
#para correto funcionamento do teste crie um arquivo .env e inclua os dados: "SECRET_KEY = QnDjPlQ0ZdRtzvbXwvzfDieNi5TqDXAT", "ALGORITHM = HS256", "ACCESS_TOKEN_EXPIRE_MINUTES = 30"
#para teste utilize como login: "username: teste@admin.com, password: 123456" --- para requisições de ADMIN, "username: teste@gmail.com, password: 123456" --- para requisições normais

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

app = FastAPI()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")
oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login-form")

from order_routes import order_router
from auth_routes import auth_router

app.include_router(order_router)
app.include_router(auth_router)
