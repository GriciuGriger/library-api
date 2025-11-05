from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import get_database_url


class Base(DeclarativeBase):
    pass


def create_db_engine():
    return create_engine(
        get_database_url(),
        pool_pre_ping=True,
        echo=False,
    )


def get_session_local(engine=None):
    engine = engine or create_db_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


engine = create_db_engine()
SessionLocal = get_session_local(engine)


# Dependency do pobierania sesji bazy danych
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
