from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .db import SessionLocal, init_db


app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def start_app():
    init_db()


@app.post("/users/signup/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/servers/", response_model=schemas.Server)
def create_server_for_user(
    user_id: int, server: schemas.ServerCreate, db: Session = Depends(get_db)
):
    return crud.create_server(db=db, server=server, user_id=user_id)


@app.get("/servers/", response_model=list[schemas.Server])
def read_servers(db: Session = Depends(get_db)):
    servers = crud.get_all_servers(db)
    return servers
