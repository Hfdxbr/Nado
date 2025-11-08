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


def get_template(id: int, session: Session) -> TableTemplate:
    return session.get(TableTemplate, id)
