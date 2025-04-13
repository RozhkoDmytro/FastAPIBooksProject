from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from typing import Annotated
import models
from fastapi import HTTPException
from fastapi import status
from fastapi import Path
from pydantic import BaseModel

app = FastAPI()

models.BaseModel.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/todos")
async def get_todos(db: db_dependency):
    todos = db.query(models.Todo).all()
    return todos


@app.get("/todos/{todo_id}", status_code=status.HTTP_201_CREATED)
async def get_todos(db: db_dependency, todo_id: int = Path(gt=0)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@app.get("/")
async def root():
    return {"message": "Hello World"}
