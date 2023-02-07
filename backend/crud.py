from sqlalchemy.orm import Session

from . import models, schemas, utils


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = utils.hash_password(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_all_servers(db: Session):
    return db.query(models.Server).all()


def create_server(db: Session, server: schemas.Server, user_id: int):
    db_server = models.Server(**server.dict(), user_id=user_id)
    db.add(db_server)
    db.commit()
    db.refresh(db_server)
    return db_server


def get_all_operations(db: Session):
    return db.query(models.Operation).all()


def create_operation(db: Session, op: schemas.Operation, user_id: int, server_id: int):
    db_op = models.Operation(**op.dict(), user_id=user_id, server_id=server_id)
    db.add(db_op)
    db.commit()
    db.refresh(db_op)
    return db_op
