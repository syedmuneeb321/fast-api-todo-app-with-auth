from sqlmodel import Session,select
from fastapi import Depends,HTTPException
from typing import Annotated
from ..Model.model import Todo,UpdateTodo,UserInDB,CreateTodo,ReadUser
from ..Utils.utils import get_session 
from .user_service import get_current_user






def create_todo(
        todo:CreateTodo,
        session:Annotated[Session,Depends(get_session)],
        user:Annotated[ReadUser,Depends(get_current_user)]
        ):
        
        if user:
            db_todo = Todo(content=todo.content,user=user)
            session.add(db_todo)
            session.commit()
            session.refresh(db_todo)
            return db_todo
            
        
    



def get_todos(user:Annotated[UserInDB,Depends(get_current_user)]):
    if user is None:
        raise HTTPException(status_code=404,detail='not user found')
    return user.todos
    



def get_todo(todo_id:int,session:Session):
     if todo_id:
          todo = session.get(Todo,todo_id)
          if todo is None:
               raise HTTPException(status_code=404,detail='Todo Not Found')
          return todo 
     
     return False
               


def update_todo(
          session:Annotated[Session,Depends(get_session)],
          user:Annotated[ReadUser,Depends(get_current_user)],
          todo:UpdateTodo,
          todo_id:int
        ):

        if user:
            db_todo = get_todo(todo_id=todo_id,session=session)
            todo_data = todo.model_dump(exclude_unset=True)
            db_todo.sqlmodel_update(todo_data)
            session.add(db_todo)
            session.commit()
            session.refresh(db_todo)
            return db_todo
        else:
           raise HTTPException(status_code=404,detail='User not found')
        
        
def toggle_todo(todo_id:int,user:Annotated[ReadUser,Depends(get_current_user)],session:Session=Depends(get_session)):
    if user:
        todo=get_todo(todo_id,session=session)
        if todo.completed:
            todo.completed = False
        else:
            todo.completed = True 

        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo
    else:
        raise HTTPException(status_code=404,detail='User not found')


def delete_todo(session:Annotated[Session,Depends(get_session)],user:Annotated[UserInDB,Depends(get_current_user)],todo_id):
    if user:
        todo =get_todo(todo_id,session)
        session.delete(todo)
        session.commit()
        return {"ok":True}        
    else:
        raise HTTPException(status_code=404,detail='User not found')






