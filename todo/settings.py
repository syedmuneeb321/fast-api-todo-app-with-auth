from starlette.config import Config 
from starlette.datastructures import Secret 


try:
    config = Config(".env")
except FileNotFoundError:
    print('create .env file')
    config = Config()

DATABASE_URL = config("DATABASE_URL",cast=Secret)
ALGORITHM = config("ALGORITHM",cast=Secret)
SECRET_KEY = config("SECRET_KEY",cast=Secret)
