
from sqlalchemy.orm import Session

from core.dbconfig import engine

session = Session(engine)
