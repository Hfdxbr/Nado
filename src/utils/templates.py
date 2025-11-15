from sqlmodel import select

from src.database import Session, TableTemplate, Template


def list_templates(session: Session) -> list[TableTemplate]:
    templates = session.exec(select(TableTemplate)).all()
    return templates


def create_template(template: Template, session: Session, user_id: int | None = None) -> TableTemplate:
    table_template = TableTemplate(**template.model_dump(), user_id=user_id)
    session.add(table_template)
    session.commit()
    session.refresh(table_template)
    return table_template


def get_user_templates(user_id: int, session: Session) -> list[TableTemplate]:
    templates = session.exec(
        select(TableTemplate).where((TableTemplate.user_id == user_id) | (TableTemplate.user_id == None))
    ).all()
    return templates


def get_template(id: int, session: Session) -> TableTemplate:
    return session.get(TableTemplate, id)


def delete_template(id: int, session: Session) -> bool:
    template = session.get(TableTemplate, id)
    if template:
        template.user_id = 0
        session.commit()
        return True
    return False
