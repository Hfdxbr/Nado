from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Annotated

engine = create_engine("sqlite:///test.db")
SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


class UserCreate(SQLModel):
    name: str
    email: str
    age: int = Field(ge=0, le=100)


class User(UserCreate, table=True):
    id: int | None = Field(primary_key=True)


class TemplateCreate(SQLModel):
    title: str
    repr: str
    default: bool


class Template(SQLModel, table=True):
    id: int = Field(primary_key=True)


class HistoryCreate(SQLModel):
    user_id: int
    seed: bytes
    templates: list[int]
    counters: list[int]


class History(SQLModel, table=True):
    id: int = Field(primary_key=True)


app = FastAPI()


@app.get("/users")
def list_users(session: SessionDep) -> list[User]:
    users = session.exec(select(User)).all()
    return users


@app.post("/users")
def post_user(user: UserCreate, session: SessionDep):
    session.add(User(**user.model_dump()))
    session.commit()
    return {"success": True}


@app.get("/users/{id}")
def get_user(id: int, session: SessionDep) -> UserCreate:
    user = session.get(User, id)
    if not user:
        raise HTTPException(status_code=404)
    return user
