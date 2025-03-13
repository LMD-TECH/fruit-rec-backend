from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session


class Base(DeclarativeBase):
    pass


sqlite_file_name = "db.db"
chaine_de_connexion = f"sqlite:///{sqlite_file_name}"

engine = create_engine(chaine_de_connexion, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session(engine)


Base.metadata.create_all(bind=engine)


def create_tables():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
