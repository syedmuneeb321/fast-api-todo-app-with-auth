from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends,Response
# from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .Utils.utils import create_db_and_tables
from .Model.model import Todo, DeleteTodo
from .Model.model import ReadUser,UserInDB,UserWithTodos,ReadUser,ReadToken
from .Service.todo_service import create_todo, update_todo,get_todos,delete_todo,toggle_todo
from .Service.user_service import create_user,login,get_current_active_user,tokens_service
from .Service.delete_table import delete_all_tables
from typing import Annotated, Union


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables..")
    create_db_and_tables()
    # delete_all_tables()
    yield


app = FastAPI(
    title="hello wordl api",
    version="0.0.1",
    servers=[
        {
            "url": "http://localhost:8000",  # ADD NGROK URL Here Before Creating GPT Action
            "description": "Development Server",
        },
    ],
    lifespan=lifespan,
)


origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}




# @app.get("/todo", response_model=list[Todo])
# def todo_read(todos: Annotated[list[Todo], Depends(read_todo)]):
#     return todos


# @app.delete("/todo/{todo_id}", response_model=DeleteTodo)
# def todo_delete(todo: Annotated[DeleteTodo, Depends(delete_todo)]):
#     return todo




# user service ends points

@app.post("/signup",response_model=ReadUser)
def user_create(user:Annotated[ReadUser,Depends(create_user)]):
    return user



@app.post("/login",response_model=ReadToken)
def user_login(user:Annotated[ReadToken,Depends(login)]):
    return user


@app.get('/user/me',response_model=ReadUser)
def read_user(user:Annotated[ReadUser,Depends(get_current_active_user)]):
    return user 


@app.get('/token',response_model=ReadToken)
def create_token(tokens:Annotated[ReadToken,Depends(tokens_service)]):
    return tokens



# todo service end points

@app.get('/todos',response_model=list[Todo])
def todo_get(todos:Annotated[list[Todo],Depends(get_todos)]):
    return todos



@app.delete("/todo/{todo_id}")
def todo_delete(todo:Annotated[dict,Depends(delete_todo)]):
    return todo


@app.post("/todo", response_model=Todo)
def todo_create(todo: Annotated[Todo, Depends(create_todo)]):
    return todo

@app.patch("/todo", response_model=Union[Todo, dict])
def todo_update(todo: Annotated[Union[dict, Todo], Depends(update_todo)]):
    return todo

@app.get('/todo',response_model=Todo)
def todo_completed(todo:Annotated[Todo,Depends(toggle_todo)]):
    return todo