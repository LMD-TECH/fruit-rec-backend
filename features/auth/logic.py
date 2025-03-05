
from fastapi import APIRouter, Response,HTTPException

from db.shema import UtilisateurBase, UtilisateurCreate
from lib.session import session
from db.models import Utilisateur
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError # j'ai ajouter


router = APIRouter(
    prefix="/api/auth",
    tags=["Auth"],
)


@router.get("/users")
def get_all_users() -> list[UtilisateurBase]:
    return session.query(Utilisateur).all()


@router.post("/login")
async def login(response: Response, data: UtilisateurBase):
    # response.set_cookie()
    return [{"username": "Rick"}, {"username": "Morty"}]
#
"""
@router.post("/register")
def register(user: UtilisateurCreate) -> UtilisateurBase:

    try:
        user_mapped = Utilisateur(**user.dict())
        session.add(user_mapped)
        session.commit()
        session.refresh(Utilisateur)
        return user
    except:
        session.rollback()
        return {"error": "Erreur d'insertion, veuillez réessayer."}
"""
@router.post("/registrer",response_model=UtilisateurBase)
def registrer (user: UtilisateurCreate) -> UtilisateurBase:
    try:
        user_mapped = Utilisateur(**user.dict())
        session.add(user_mapped)
        session.commit()
        session.refresh(user_mapped)
        return UtilisateurBase(**user_mapped._dict_)
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Erreur d'insertion, veuillez réessayer") from e

