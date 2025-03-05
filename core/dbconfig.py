from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, DeclarativeBase


class Base(DeclarativeBase):
    pass


sqlite_file_name = "db.db"
chaine_de_connexion = f"sqlite:///{sqlite_file_name}"

engine = create_engine(chaine_de_connexion, echo=True)


def create_tables():
    Base.metadata.create_all(bind=engine)
