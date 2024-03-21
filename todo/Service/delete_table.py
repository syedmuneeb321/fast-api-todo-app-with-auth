from ..Model.model import Todo,DeleteTodo 
from ..Utils.utils import engine 
from sqlmodel import SQLModel 



def delete_all_tables():
    SQLModel.metadata.drop_all(engine)

