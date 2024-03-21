from passlib.context import CryptContext
from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from sqlmodel import Session,select
from typing import Annotated
from datetime import datetime, timedelta, timezone
from jose import JWTError,jwt

from ..Model.model import UserInDB,ReadUser,CreateUser  ,Todo,CreateToken
from ..Utils.utils import get_session
from ..settings import SECRET_KEY,ALGORITHM



pwd_context = CryptContext(schemes=["bcrypt"],deprecated='auto') 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 7        

def get_password_hash(password:str)->str:
    return pwd_context.hash(password) 

def verify_password(plain_password:str,hashed_password:str)->str:
    return pwd_context.verify(plain_password,hashed_password)



def create_user(session:Annotated[Session,Depends(get_session)],user:CreateUser):

    user_exit = session.exec(select(UserInDB).where(UserInDB.username==user.username or UserInDB.email == user.email)).first() 

    if user_exit:   
        raise HTTPException(status_code=400,detail="Email or Username already registered")

    hashed_password = get_password_hash(password=user.password)
    extra_data = {"hashed_password":hashed_password}
    db_user = UserInDB.model_validate(user,update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user



def get_user(username:str,session:Session):
        if username is None:
            raise  HTTPException(status_code=404, detail="Username not provided")
        
        user = session.exec(select(UserInDB).where(UserInDB.username == username)).first()

        if not user:
            raise HTTPException(status_code=404,detail='User not found')
        return user 


def get_user_by_email(email:str,session:Session):
    if email is None:
            raise  HTTPException(status_code=404, detail="Email not provided")
    user = session.exec(select(UserInDB).where(UserInDB.email == email)).first()
    if not email:
        raise HTTPException(status_code=404,detail='user not found')
    
    return user


def authenticate_user(username:str,password:str,session:Session):
    user = get_user(username=username,session=session)
    
    verify = verify_password(password,user.hashed_password)

    if not verify:
        return False 
    
    return user 


def create_access_token(data:dict,expire_time:timedelta|None=None):
    encode_data = data.copy()
    if expire_time:
        expire = datetime.now(timezone.utc) + expire_time
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    
    encode_data.update({"exp": expire})
   

    encoded_jwt = jwt.encode(encode_data,key=f"{SECRET_KEY}",algorithm=f"{ALGORITHM}")
    
    
    return encoded_jwt



def create_refresh_token(data:dict,expire_time:timedelta|None=None):
    encode_data = data.copy()
    if expire_time:
        expire = datetime.now(timezone.utc) + expire_time
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=7)
    
    encode_data.update({"exp":expire})

    endoce_jwt = jwt.encode(encode_data,f"{SECRET_KEY}",algorithm=f"{ALGORITHM}")

    return endoce_jwt



def validate_refresh_token(token:Annotated[str,Depends(oauth2_scheme)],session:Session=Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token,key=f"{SECRET_KEY}",algorithms=[f"{ALGORITHM}"])

        email = payload.get('email')

        if not email: 
            raise credentials_exception 
        
    except JWTError:
        raise credentials_exception

    user = get_user_by_email(email,session)

    if not user:
        raise credentials_exception 
    
    return user



def tokens_service(user:Annotated[UserInDB,Depends(validate_refresh_token)]):
    if not user:
        raise HTTPException(status_code=404,detail='Not provide a username')
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(data={"sub":user.username},expire_time=access_token_expires) 


    refresh_token = create_refresh_token(data={"email":user.email},expire_time=refresh_token_expires)

    return CreateToken(token=access_token,token_type="bearer",expires_in=int(access_token_expires.total_seconds()),refresh_token=refresh_token)



def login( 
        form_data:Annotated[OAuth2PasswordRequestForm,Depends()],
        session:Annotated[Session,Depends(get_session)]):
    
    user = authenticate_user(form_data.username,
                            form_data.password,
                            session)

    if not user:
        raise HTTPException(
             status_code=401,
            detail="Incorrect username or password",
            # headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(data={"sub":user.username},expire_time=access_token_expires) 


    refresh_token = create_refresh_token(data={"email":user.email},expire_time=refresh_token_expires)

    return CreateToken(token=access_token,token_type="bearer",expires_in=int(access_token_expires.total_seconds()),refresh_token=refresh_token)
    




def get_current_user(token:Annotated[str,Depends(oauth2_scheme)],session:Annotated[Session,Depends(get_session)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token,f"{SECRET_KEY}",algorithms=[f"{ALGORITHM}"])
        username:str|None = payload.get('sub')
        expire = payload.get('exp')
        if username is None:
            raise credentials_exception 
        
        # print(expire)
        # token_data = TokenData(username=username)

        # if token_data.username is None:
        #     raise credentials_exception
    

    except JWTError:
        raise credentials_exception
    
    user = get_user(username,session)

    if user is None:
        raise credentials_exception 
    
    return user




def get_current_active_user(current_user:Annotated[ReadUser,Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return current_user
    