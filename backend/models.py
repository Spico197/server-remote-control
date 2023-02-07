import datetime
from typing import Optional

from sqlmodel import (
    SQLModel,
    Field,
    Relationship,
    Column,
    String,
    Integer,
    DateTime,
    func,
)


class UserBase(SQLModel):
    username: str = Field(
        sa_column=Column(String, index=True, unique=True, nullable=False)
    )


class UserCreate(UserBase):
    hashed_password: str = Field(sa_column=Column(String))


class User(UserCreate, table=True):
    __tablename__ = "user"
    id: int = Field(default=None, sa_column=Column(Integer, primary_key=True, autoincrement=True))
    # servers: list["Server"] = Relationship(back_populates="user")
    # operations: list["Operation"] = Relationship(back_populates="user")


# class ServerBase(SQLModel):
#     ip: str
#     ssh_port: int = 22
#     username: str
#     password: str
#     manage_url: str
#     manage_username: str
#     manage_type: str
#     memo: str = ""


# class ServerCreate(ServerBase):
#     pass


# class Server(ServerCreate, table=True):
#     __tablename__ = "server"

#     id: int = Field(default=None, sa_column=Column(Integer, primary_key=True, autoincrement=True))
#     user: Optional[User] = Relationship(back_populates="servers")
#     user_id: int = Field(default=None, foreign_key="user.id")
#     operations: list["Operation"] = Relationship(back_populates="server")


# class OperationBase(SQLModel):
#     record: str
#     create_datetime: datetime.datetime = Field(
#         sa_column=Column(DateTime, server_default=func.now(), nullable=False)
#     )


# class OperationCreate(OperationBase):
#     pass


# class Operation(OperationCreate, table=True):
#     __tablename__ = "operation"

#     id: int = Field(sa_column=Column(Integer, primary_key=True, autoincrement=True))

#     user: User = Relationship(back_populates="operations")
#     user_id: int = Field(foreign_key="user.id")

#     server: Server = Relationship(back_populates="operations")
#     server_id: int = Field(foreign_key="server.id")
