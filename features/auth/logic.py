
from datetime import datetime
from fastapi import APIRouter, Response, Request, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.security import OAuth2PasswordBearer
from core.lib.session import session
from pydantic import EmailStr
from typing import Annotated
from .validations import UtilisateurLogin, UtilisateurBase, UtilisateurCreate, UtilisateurReset, UtilisateurUpdatePassword
from .models import Utilisateur
from .utils import get_password_hash, verify_password, authenticate_user, create_access_token, get_user
from datetime import datetime, timedelta
import os
from ..uploads.logic import create_image_file
from dotenv import load_dotenv
import jwt


load_dotenv()

# Endpoints fo
# Group d'endpoints
router = APIRouter(
    prefix="/api/auth",
    tags=["Auth"],
)

# Endpoint pour recuperer touts les utilsateur

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = os.getenv("ALGORITHM", "")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 10))
UPLOADS_DIR = os.getenv("UPLOADS_DIR", "static")

os.makedirs(UPLOADS_DIR, exist_ok=True)


@router.get("/users")
def get_all_users() -> list[UtilisateurBase]:
    return session.query(Utilisateur).all()


@router.post("/login")
async def login(response: Response, data: UtilisateurLogin):
    try:
        mot_de_passe = data.mot_de_passe
        email = data.email
        print("User_Authenticated", email)
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


# TODO: demain on attaque

@router.post("/reset-password")
async def reset_password(response: Response, data: UtilisateurReset):
    try:
        return {'status': True, "datas": data}
    except Exception as e:
        return {'status': False}


@router.post("/update-password")
async def update_password(response: Response, request: Request, data: UtilisateurUpdatePassword):

    try:
        token = request._cookies.get("token")
        if not token:
            raise Exception("Vous n'êtes pas connecté!")

        payload_jwt_decoded = jwt.decode(
            token, key=SECRET_KEY, algorithms=[ALGORITHM])

        current_time = datetime.utcnow()
        expiration_time = datetime.utcfromtimestamp(payload_jwt_decoded["exp"])

        if expiration_time < current_time:
            raise Exception("Le token a expiré!")

        if not payload_jwt_decoded:
            raise Exception("Token invalide!")

        user = get_user(payload_jwt_decoded["sub"])
        if data.nouveau_de_passe_actuel != data.confirm_nouveau_de_passe_actuel:
            raise Exception(
                "Mot de passe et mot de passe confirmation ne correspoondent pas !")

        if not verify_password(data.mot_de_passe_actuel, user.mot_de_passe):
            raise Exception(
                "Mot de passe actuel et mot de passe recu correspoondent pas !")

        user.mot_de_passe = get_password_hash(data.nouveau_de_passe_actuel)
        session.add(user)
        session.commit()
        session.refresh(user)

        return {'status': True, "user": user, "data": data}
    except Exception as e:
        print(e)
        return {'status': False, "error": str(e)}


# Changement du mot de passe

@router.post("/register")
async def register(
    nom_famille: Annotated[str, Form()],
    numero_telephone: Annotated[str, Form()],
    prenom: Annotated[str, Form()],
    email: Annotated[EmailStr, Form()],
    mot_de_passe: Annotated[str, Form()],
    confirm_mot_de_passe: Annotated[str, Form()],
    photo_profile: Annotated[UploadFile | None, File(
        description="A file read as UploadFile")] = None,
):

    try:
        if mot_de_passe != confirm_mot_de_passe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Les mots de passe ne correspondent pas."
            )

        image_created_url = None
        if photo_profile:
            try:
                image_created_url = create_image_file(photo_profile)
            except Exception as e:
                pass

        mot_de_passe = get_password_hash(mot_de_passe)
        user = {
            "mot_de_passe": mot_de_passe,
            "nom_famille": nom_famille,
            "numero_telephone": numero_telephone,
            "prenom": prenom,
            "email": email,
            "photo_profile": image_created_url
        }
        user_mapped = Utilisateur(**user)
        session.add(user_mapped)
        session.commit()
        session.refresh(user_mapped)
        return {"data": user}
    except Exception as e:
        session.rollback()
        return {"error": "Erreur d'insertion, veuillez réessayer.", "e": str(e)}
