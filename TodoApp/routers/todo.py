from fastapi import Depends, HTTPException, status, Path, APIRouter
from sqlalchemy.orm import Session
from database import SessionLocal
from typing import Annotated
import models
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
    responses={404: {"description": "Not found"}},
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/")
async def get_todos(db: db_dependency):
    todos = db.query(models.Todo).all()
    return todos


@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todos(db: db_dependency, todo_id: int = Path(gt=0)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )
    return todo


class TodoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=20)
    description: str = Field(max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool = Field(default=False)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo: TodoRequest):
    todo_model = models.Todo(**todo.model_dump())
    db.add(todo_model)
    db.commit()
    return todo_model


@router.put("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency, todo: TodoRequest, todo_id: int = Path(gt=0)):
    todo_model = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete
    db.commit()
    return todo_model


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )
    db.delete(todo_model)
    db.commit()


@router.get("/")
async def root():
    return {"message": "Hello World"}
