from fastapi import FastAPI
from database import engine

import models

from routers import auth, todo

app = FastAPI()

models.BaseModel.metadata.create_all(bind=engine)
app.include_router(router=auth.router)

app.include_router(router=todo.router)
