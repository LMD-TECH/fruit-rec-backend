
from datetime import datetime
from fastapi import APIRouter, Response, Request, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.security import OAuth2PasswordBearer
from core.lib.session import session
from pydantic import EmailStr
from typing import Annotated
from .validations import UtilisateurLogin, UtilisateurBase, UtilisateurForgotPassword, UtilisateurReset, UtilisateurUpdatePassword
from .models import Utilisateur
from .utils import get_password_hash, verify_password, authenticate_user, create_access_token, get_user
from datetime import datetime, timedelta, timezone
import os
from ..uploads.logic import create_image_file
from dotenv import load_dotenv
import jwt
from core.utils import make_message, send_email, generate_otp_code, validate_phone_number
from sqlalchemy.exc import IntegrityError

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


@router.post("/forgot-password")
async def forgot_password(response: Response, data: UtilisateurForgotPassword):
    try:
        email = data.email
        user = get_user(email)
        if not user:
            raise HTTPException(detail="User not found!", status_code=404)

        APP_URL = os.getenv('APP_URL', "")+"/auth/reset-password"
        code = generate_otp_code()
        user.code_otp = code
        exp = timedelta(minutes=5)
        token = create_access_token({"code_otp": code}, exp)

        session.add(user)
        session.commit()
        session.refresh(user)
        link = APP_URL + f'?token={token}'
        content = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
                        <div style="background-color: #fff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                        <p style="font-size: 16px; color: #333;">Bonjour,</p>
                        <p style="font-size: 16px; color: #333;">
                            Cliquez sur le lien ci-dessous pour réinitialiser votre mot de passe :
                        </p>
                        <a href="{link}" style="font-size: 16px; color: #1E90FF; text-decoration: none;">Réinitialiser mon mot de passe</a>
                        </div>
                    </body>
                    </html>
                    """

        msg = make_message(
            "Code de verification", content, to=email)
        email_infos = send_email(msg, email,)
        return {'status': True, "email": email_infos, "token": token}

    except HTTPException as e:
        response.status_code = e.status_code
        return {"detail": e.detail}
    except Exception as e:
        response.status_code = 500
        return {'status': False, "error_message": str(e)}


@router.post("/reset-password/{token}")
async def reset_password(token: str, data: UtilisateurReset):

    payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
    code_otp = payload.get("code_otp")

    user = session.query(Utilisateur).filter(
        Utilisateur.code_otp == code_otp).first()

    if not user:
        raise HTTPException(detail="User not found", status_code=404)

    new_password = data.new_password
    confirm_new_password = data.confirm_new_password
    if new_password != confirm_new_password:
        raise HTTPException(
            detail="Les mots de passe ne correspondent pas!", status_code=400)

    user.mot_de_passe = new_password
    user.code_otp = None
    user.code_otp_expiration = None
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"status": True, "user": user}


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

        if not verify_password(data.mot_de_passe_actuel, user.mot_de_passe):
            raise Exception(
                "Mot de passe actuel et mot de passe recu correspoondent pas !")

        user.mot_de_passe = get_password_hash(data.nouveau_de_passe)
        session.add(user)
        session.commit()
        session.refresh(user)

        return {'status': True, "user": user, "data": data}
    except Exception as e:
        print(e)
        return {'status': False, "error": str(e)}


@router.post("/register")
async def register(
    response: Response,
    nom_famille: Annotated[str, Form()],
    numero_telephone: Annotated[str, Form()],
    prenom: Annotated[str, Form()],
    email: Annotated[EmailStr, Form()],
    mot_de_passe: Annotated[str, Form()],
    photo_profile: Annotated[UploadFile | str, File(
        description="A file read as UploadFile")] = "",
):
    try:

        image_created_url = None
        if photo_profile:
            try:
                image_created_url = create_image_file(photo_profile)
            except Exception as e:
                pass
        validate_phone_number(numero_telephone)
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

        APP_URL = os.getenv('APP_URL', "") + "/login"
        content = f"""
                    <html lang='fr'>
                    <head>
                        <meta charset="UTF-8">
                        <title>Bienvenue !</title>
                    </head>
                    <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f3f4f6;">
                        <div style="max-width: 600px; margin: 20px auto; background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
                            <h1 style="color: #4f46e5;">Bienvenue à bord !</h1>
                            <p style="color: #374151; line-height: 1.6;">
                                Bonjour {prenom},
                            </p>
                            <p style="color: #374151; line-height: 1.6;">
                                Nous sommes ravis de vous accueillir parmi nous ! Vous avez maintenant accès à toutes nos fonctionnalités. Connectez-vous dès maintenant pour explorer votre espace personnalisé :
                            </p>
                            <a href="{APP_URL}/auth/login" 
                            style="display: inline-block; padding: 10px 20px; margin-top: 20px; color: white; background-color: #4f46e5; text-decoration: none; border-radius: 5px;">
                                Accéder à votre compte
                            </a>
                            <p style="color: #374151; line-height: 1.6;">
                                Si vous avez besoin d'aide ou si vous avez des questions, notre équipe est à votre disposition.
                            </p>
                            <p style="color: #374151; line-height: 1.6;">
                                À très bientôt,<br>L'équipe
                            </p>
                        </div>
                    </body>
                    </html>
                """
        msg = make_message(
            "Votre compte a été crée avec succès.", content, to=email)
        email_result = send_email(msg, email,)

        return {"data": user, "email": email_result}
    except HTTPException as e:
        response.status_code = e.status_code
        return e

    except IntegrityError as e:
        response.status_code = 500
        return {"error": "Cet email ou ce numéro de téléphone existe déjà!"}
    except Exception as e:
        response.status_code = 500
        return {"error": str(e)}
    finally:
        session.rollback()


@router.post("/delete-user")
def delete_user(email: str):
    user = get_user(email)
    session.delete(user)
    session.commit()
    return {"success": True}
