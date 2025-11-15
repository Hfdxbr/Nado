from os import urandom

from src.database import Generation, Session, TableGeneration
from src.utils.users import get_by_id


def list_generations(user_id: int, session: Session) -> list[TableGeneration] | None:
    user = get_by_id(user_id, session)
    if user is not None:
        return user.generations


def create_genertion(id: int, generation: Generation, session: Session) -> TableGeneration:
    table_generation = TableGeneration(**generation.model_dump(), user_id=id, seed=urandom(8))
    session.add(table_generation)
    session.commit()
    session.refresh(table_generation)
    return table_generation
