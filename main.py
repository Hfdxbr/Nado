from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import (
    Field,
    Session,
    SQLModel,
    create_engine,
    select,
    Relationship,
    JSON,
    Column,
)
from pydantic import EmailStr
from typing import Annotated

engine = create_engine("sqlite:///database.sqlite")
SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


class Template(SQLModel):
    title: str
    repr: str


class TableTemplate(Template, table=True):
    id: int = Field(primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="tableuser.id")
    user: "TableUser" = Relationship(back_populates="templates")


class User(SQLModel):
    email: EmailStr
    password_hash: bytes


class TableUser(User, table=True):
    id: int = Field(primary_key=True)
    templates: list["TableTemplate"] = Relationship(back_populates="user")
    generations: list["TableGeneration"] = Relationship(back_populates="user")


class Generation(SQLModel):
    seed: bytes
    templates: list[int] = Field(default_factory=list, sa_column=Column(JSON))
    counters: list[int] = Field(default_factory=list, sa_column=Column(JSON))


class TableGeneration(Generation, table=True):
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="tableuser.id")
    user: "TableUser" = Relationship(back_populates="generations")


app = FastAPI()


@app.get("/users")
def list_users(session: SessionDep) -> list[TableUser]:
    users = session.exec(select(TableUser)).all()
    return users


@app.post("/users")
def post_user(user: User, session: SessionDep):
    table_user = TableUser(**user.model_dump())
    session.add(table_user)
    session.commit()
    session.refresh(table_user)
    return {"success": True, "user_id": table_user.id}


@app.get("/users/{id}")
def get_user(id: int, session: SessionDep) -> User:
    user = session.get(TableUser, id)
    if not user:
        raise HTTPException(status_code=404)
    return user


@app.get("/templates")
def list_templates(session: SessionDep) -> list[TableTemplate]:
    users = session.exec(select(TableTemplate)).all()
    return users


@app.post("/templates")
def post_template(template: Template, session: SessionDep):
    table_template = TableTemplate(**template.model_dump())
    session.add(table_template)
    session.commit()
    session.refresh(table_template)
    return {"success": True, "template_id": table_template.id}


@app.get("/templates/{id}")
def get_template(id: int, session: SessionDep) -> Template:
    user = session.get(TableTemplate, id)
    if not user:
        raise HTTPException(status_code=404)
    return user