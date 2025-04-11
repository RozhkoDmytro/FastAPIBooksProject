from database import BaseModel
from sqlalchemy import Column, Integer, String, Boolean


class Todo(BaseModel):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    complete = Column(Boolean, default=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    prioryty = Column(Integer, nullable=False)
