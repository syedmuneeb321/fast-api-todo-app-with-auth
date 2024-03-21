from fastapi.testclient import TestClient
from sqlmodel import Session,create_engine,SQLModel
from ..todo.main import app 

from ..todo.Model.model import Todo
from ..todo.Utils.utils import get_session
import pytest 


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(url='sqlite:///test.db',echo=True,)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session:Session):
    def get_session_overide():
        return session 
    
    app.dependency_overrides[get_session] = get_session_overide
    client = TestClient(app)
    yield client 
    app.dependency_overrides.clear()


@pytest.fixture(name="header")
def token_fixture(client:TestClient):
    user_login_data = {
        "username":"ali",
        "password":"ali123"
    }

    token_response = client.post("/login",data=user_login_data)

    token_data = token_response.json()
    header = {'Authorization': f'Bearer {token_data["token"]}',
       'Content-Type': 'application/json'}
    
    return header



# def test_main():
#     client = TestClient(app)

#     response = client.get("/")
#     assert response.status_code == 200 
#     assert response.json() == {"Hello": "World"}

def test_post(client:TestClient,header):
    

    create_todo_data = {"content":"testing"}

    response = client.post("/todo/",json=create_todo_data,headers=header)
    todo_data = response.json()
    assert response.status_code == 200
    assert todo_data['content'] == create_todo_data['content']
    assert todo_data['id'] is not None
    


    
        
def test_read_todo(client:TestClient,header):

    response = client.get('/todos',headers=header)
    data = response.json()
    assert response.status_code == 200 
    assert len(data) == 1
    


def test_update_todo(client:TestClient,header):
    update_todo = {
        "content":"updata todo completed"
    }

    response = client.patch('/todo',params={"todo_id":1},json=update_todo,headers=header)
    data = response.json()
    assert response.status_code == 200 
    assert data['content'] == update_todo['content']

def test_delete_todo(client:TestClient,header):
    
    
    
    response = client.delete("/todo/1",headers=header)
    data = response.json()
    assert response.status_code == 200
    assert data['ok'] == True 