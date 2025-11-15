from fastapi import APIRouter, HTTPException

from src.api import SessionDep
from src.database import TableTemplate, Template
import src.utils.templates as ut

router = APIRouter(prefix="/api")


@router.get("/templates")
def list_templates(session: SessionDep) -> list[TableTemplate]:
    return ut.list_templates(session)


@router.post("/templates")
def post_template(template: Template, session: SessionDep):
    table_template = ut.create_template(template, session)
    return {"success": True, "template_id": table_template.id}


@router.get("/templates/{id}")
def get_template(id: int, session: SessionDep) -> Template:
    template = ut.get_template(id, session)
    if not template:
        raise HTTPException(status_code=404)
    return template

@router.delete("/templates/{id}")
def delete_template(id: int, session: SessionDep):
    success = ut.delete_template(id, session)
    if not success:
        raise HTTPException(status_code=404)
    return {"success": True}