from pathlib import Path

from pydantic import Base64Bytes, EmailStr
from sqlmodel import JSON, Column, Field, Relationship, Session, SQLModel, create_engine


class Template(SQLModel):
    title: str
    repr: str


class TableTemplate(Template, table=True):
    id: int = Field(primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="tableuser.id")
    user: "TableUser" = Relationship(back_populates="templates")


class PublicUser(SQLModel):
    email: EmailStr


class PrivateUser(PublicUser):
    password: str


class TableUser(PublicUser, table=True):
    id: int = Field(primary_key=True)
    password_hash: Base64Bytes
    templates: list["TableTemplate"] = Relationship(back_populates="user")
    generations: list["TableGeneration"] = Relationship(back_populates="user")


class Generation(SQLModel):
    templates: list[int] = Field(default_factory=list, sa_column=Column(JSON))
    counters: list[int] = Field(default_factory=list, sa_column=Column(JSON))


class TableGeneration(Generation, table=True):
    id: int = Field(primary_key=True)
    seed: Base64Bytes
    user_id: int = Field(foreign_key="tableuser.id")
    user: "TableUser" = Relationship(back_populates="generations")


path = Path(__file__).parent / "database.sqlite"
engine = create_engine(f"sqlite:///{path}")
SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
