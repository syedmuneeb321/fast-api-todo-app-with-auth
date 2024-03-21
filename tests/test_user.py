from fastapi.testclient import TestClient
from sqlmodel import Session,create_engine,SQLModel
from ..todo.main import app 
from ..todo.Model.model import UserInDB,CreateUser,ReadUser
from ..todo.Utils.utils import get_session
import pytest


@pytest.fixture(name='session')
def session_fixture():
    engine = create_engine(url='sqlite:///test.db')
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session 

    
@pytest.fixture(name='client')
def client_fixture(session:Session):
    def get_session_overide():
        return session 
    
    app.dependency_overrides[get_session] = get_session_overide 
    
    client = TestClient(app)

    yield client 

    app.dependency_overrides.clear()



def test_user_post(client:TestClient):
    user_data = {
        "username":"ali",
        "email":"ali@gmail.com",
        "password":"ali123",
        "age":20
    }

    response = client.post("/signup",json=user_data)
    data = response.json()

    assert response.status_code == 200 
    assert data['username'] == user_data['username']
    assert data['email'] == user_data['email']
    assert data['age'] == user_data['age']
    assert data['id'] is not None

def test_user_login(client:TestClient):

    user_login_data = {
        "username":"ali",
        "password":"ali123"
    }

    

    token_response = client.post("/login",data=user_login_data)

    token_data = token_response.json()
    header = {'Authorization': f'Bearer {token_data["token"]}',
       'Content-Type': 'application/json'}
    
    user_response = client.get('/user/me',headers=header)
    user_data = user_response.json()
    assert token_response.status_code == 200 
    assert user_response.status_code == 200
    assert token_data['token'] == token_data['token']
    assert token_data['refresh_token'] is not None 
    assert user_data['username'] == user_login_data['username']
    assert user_data['email'] == "ali@gmail.com"
    assert user_data['age'] == 20
    






    
    