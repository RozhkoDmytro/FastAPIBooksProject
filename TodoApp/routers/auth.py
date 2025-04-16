from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel, Field, EmailStr, SecretStr
from models import Users
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "c975a719772415d3aca02fd77629ec71bf632f81fd90b107e913fa828b430603"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: EmailStr
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    role: str = Field(min_length=3, max_length=20)
    password: SecretStr
    is_active: bool = Field(default=True)


def authenticate_user(username: str, password: str, db: db_dependency):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, expires_delta: int = None):
    encode = {"sub": username, "id": user_id}
    if expires_delta:
        expire = datetime.now() + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(db: db_dependency, token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = db.query(Users).filter(Users.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user: CreateUserRequest):

    if db.query(Users).filter(Users.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(Users).filter(Users.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    user_model = Users(
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        hashed_password=bcrypt_context.hash(user.password.get_secret_value()),
        is_active=True,
    )
    db.add(user_model)
    db.commit()
    return user_model


@router.post("/token", status_code=status.HTTP_200_OK)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    jwt_token = create_access_token(user.username, user.id)
    return {"access_token": jwt_token, "token_type": "bearer"}
