from hashlib import md5

from sqlmodel import select

from src.database import PrivateUser, Session, TableUser

SALT = "lol-kek-cheburek "


class UserExists(RuntimeError):
    pass


def make_hash(user: PrivateUser):
    return md5((SALT + user.email + user.password).encode()).digest()


def get_by_id(id: int, session: Session) -> TableUser | None:
    return session.get(TableUser, id)


def get_by_email(email: str, session: Session) -> TableUser | None:
    smt = select(TableUser).where(TableUser.email == email)
    return session.exec(smt).first()


def exists(user: TableUser | None) -> bool:
    return user is not None


def create_user(user: PrivateUser, session: Session) -> TableUser:
    if exists(get_by_email(user.email, session)):
        raise UserExists(f"User with this email {user.email} already exists")
    table_user = TableUser(**user.model_dump(), password_hash=make_hash(user))
    session.add(table_user)
    session.commit()
    session.refresh(table_user)
    return table_user


def list_users(session: Session) -> list[TableUser]:
    return session.exec(select(TableUser)).all()
