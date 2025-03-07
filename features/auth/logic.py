
from fastapi import APIRouter, Response, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from core.dbconfig import engine
from core.lib.session import session
from sqlalchemy import select
from typing import Annotated
from .validations import UtilisateurLogin, UtilisateurBase, UtilisateurCreate, UtilisateurReset, TokenData
from .models import Utilisateur
from .utils import get_password_hash, verify_password
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone, timedelta
import jwt

# Endpoints fo
# Group d'endpoints
router = APIRouter(
    prefix="/api/auth",
    tags=["Auth"],
)



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# TO DO : créer un fichier .env pour stocker ses informations 
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # Arbitraire pour l'instant

# Endpoint pour recuperer touts les utilsateur(pas important voir l'ensemble des utilisateurs)
@router.get("/users")
def get_all_users() -> list[UtilisateurBase]:
    return session.query(Utilisateur).all()


def authenticate_user(email: str, mot_de_passe: str):
    user = get_user(email)
    if not user:
        return False

    mot_de_passe_correspond = verify_password(mot_de_passe, user.mot_de_passe)
    if not mot_de_passe_correspond:
        return False

    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user(email: str):
    return session.query(Utilisateur).filter(
        Utilisateur.email == email).first()


@router.post("/login")
async def login(response: Response, data: UtilisateurLogin):
    try:
        mot_de_passe = data.mot_de_passe
        email = data.email
        user_authenticated = authenticate_user(email, mot_de_passe)
        if not user_authenticated:
            return {"error": "invalid login"}

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_authenticated.email}, expires_delta=access_token_expires
        )

        response.set_cookie(key="token", value=access_token, httponly=True)
        return {'status': True, "message": "Utilsateur connecté avec success."}
    except Exception as e:
        print(e)
        response.status_code = 500
        return {'status': False, "message": "Erreur de connexion", "error": str(e)}


@router.post("/reset-password")
async def reset_password(response: Response, data: UtilisateurReset):
    try:
        return {'status': True, "data": data}
    except Exception as e:
        return {'status': False}

# To Do : récuperation de la photo de profil
@router.post("/register")
def register(user: UtilisateurCreate):

    try:
        user.mot_de_passe = get_password_hash(user.mot_de_passe)
        user_mapped = Utilisateur(**user.dict())
        session.add(user_mapped)
        session.commit()
        session.refresh(user_mapped)
        return {"data": user}
    except Exception as e:
        session.rollback()
        return {"error": "Erreur d'insertion, veuillez réessayer.", "e": str(e)}
