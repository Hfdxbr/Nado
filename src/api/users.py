from fastapi import APIRouter, HTTPException, Response, Request
from fastapi.responses import RedirectResponse
from pydantic import EmailStr
from sqlmodel import Field, SQLModel

import src.utils.generations as ug
import src.utils.users as uu
from src.api import SessionDep
from src.database import Generation, PrivateUser, TableGeneration, TableUser

router = APIRouter(prefix="/api")


class DisplayUser(SQLModel):
    email: EmailStr
    templates: int = Field(title="#templates")
    generations: int = Field(title="#generations")


@router.get("/users")
def list_users(session: SessionDep) -> list[DisplayUser]:
    table_users = uu.list_users(session)
    users = [
        DisplayUser(email=user.email, templates=len(user.templates), generations=len(user.generations))
        for user in table_users
    ]
    return users


@router.post("/users")
def create_user(user: PrivateUser, session: SessionDep):
    try:
        table_user = uu.create_user(user, session)
    except uu.UserExists as ex:
        raise HTTPException(status_code=400, detail=str(ex))
    return {"success": True, "user_id": table_user.id}


@router.post("/login")
def login_user(user: PrivateUser, session: SessionDep, response: Response):
    table_user = uu.get_by_email(user.email, session)
    if table_user is None:
        raise HTTPException(404)
    if table_user.password_hash != uu.make_hash(user):
        raise HTTPException(401)
    response.set_cookie("user-id", str(table_user.id))


@router.get("/user")
def get_user(request: Request) -> TableUser:
    id = request.cookies.get("user-id")
    if id is None:
        raise HTTPException(401)
    return RedirectResponse(f"/users/{id}")


@router.get("/users/{id}")
def get_user_by_id(id: int, session: SessionDep) -> TableUser:
    user = uu.get_by_id(id, session)
    if not user:
        raise HTTPException(status_code=404)
    return user


@router.get("/users/{id}/generations")
def list_generations(id: int, session: SessionDep) -> list[TableGeneration]:
    generations = ug.list_generations(id, session)
    if not generations:
        raise HTTPException(status_code=404)
    return generations


@router.post("/users/{id}/generations")
def create_generation(id: int, generation: Generation, session: SessionDep):
    table_generation = ug.create_generation(id, generation, session)
    return {"success": True, "generation_id": table_generation.id}
