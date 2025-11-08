from hashlib import md5

from sqlmodel import select

from src.database import PrivateUser, Session, TableUser

SALT = "lol-kek-cheburek "


class UserExists(RuntimeError):
    pass


def exists_by_email(email: str, session: Session) -> bool:
    smt = select(TableUser).where(TableUser.email == email)
    return session.exec(smt).first() is not None


def exists_by_id(id: int, session: Session) -> bool:
    return session.get(TableUser, id) is not None


def create_user(user: PrivateUser, session: Session) -> TableUser:
    if exists_by_email(user.email, session):
        raise UserExists(f"User with this email {user.email} already exists")
    password_hash = md5((SALT + user.email + user.pasword).encode()).digest()
    table_user = TableUser(**user.model_dump(), password_hash=password_hash)
    session.add(table_user)
    session.commit()
    session.refresh(table_user)
    return table_user


def get_user(id: int, session: Session) -> TableUser | None:
    return session.get(TableUser, id)


def list_users(session: Session) -> list[TableUser]:
    return session.exec(select(TableUser)).all()
