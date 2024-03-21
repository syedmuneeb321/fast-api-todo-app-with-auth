from ..Model.model import Todo,UserInDB
from sqlmodel import SQLModel,create_engine,Session 
from ..settings import DATABASE_URL



# db_name = 'database.db'
# db_url = f"sqlite://{db_name}"
# connection_string = f"sqlite:///database.db"
connection_string = str(DATABASE_URL).replace("postgresql","postgresql+psycopg")



engine = create_engine(url=connection_string)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session