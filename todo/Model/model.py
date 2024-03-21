from sqlmodel import Field, SQLModel,Relationship 
from typing import Optional,List


class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(index=True)
    completed:bool|None = False
    user_id:int|None = Field(default=None,foreign_key='userindb.id')
    user:Optional['UserInDB'] = Relationship(back_populates="todos")
    


class DeleteTodo(SQLModel):
    ok:bool|None = True 
    detail:str|None = None 

class UpdateTodo(SQLModel):
    content:str|None = None

class CreateTodo(SQLModel):
    content: str


class User(SQLModel):
    username:str
    email:str
    age:int|None=None
    disabled:bool=False

    

class UserInDB(User,table=True):
    id:int|None = Field(default=None,primary_key=True)
    hashed_password:str 
    todos:List[Todo] = Relationship(back_populates='user')
    

class CreateUser(User):
    password:str 
   

class ReadUser(User):
    id:int
    



class CreateToken(SQLModel):
    token:str
    refresh_token: str 
    token_type:str
    expires_in:int

class ReadToken(CreateToken):
    pass




# class UpdateUser(SQLModel):
#     username:str|None = None
#     email: str|None = None
#     age:int|None = None 
#     disabled:bool = False
#     password: str|None = None


class UserWithTodos(ReadUser):
    todos:List[Todo] = []