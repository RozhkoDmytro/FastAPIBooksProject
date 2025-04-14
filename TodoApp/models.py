from database import BaseModel
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


class User(BaseModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, nullable=False)


class Todo(BaseModel):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    complete = Column(Boolean, default=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    priority = Column(Integer, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
