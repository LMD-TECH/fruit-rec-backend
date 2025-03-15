
from datetime import datetime
from fastapi import APIRouter, Response, Request, Depends, HTTPException, status, File, UploadFile, Form, Cookie
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from typing import Annotated, Optional
from core.jinja2.env import env
from features.auth.utils import verify_jwt
from core.dbconfig import get_db
from .validations import UtilisateurLogin, UtilisateurBase, UtilisateurForgotPassword, UtilisateurReset, UtilisateurUpdatePassword, AuthenticationResult
from .models import Utilisateur
from .utils import get_password_hash, verify_password, authenticate_user, create_access_token
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin
import os
from ..uploads.logic import create_image_file
from dotenv import load_dotenv
import jwt
from core.utils import (generate_otp_code, get_auth_token_in_request, get_user,
                        get_user_from_session, make_message, send_email, validate_phone_number)
from sqlalchemy.exc import IntegrityError

load_dotenv()

# Endpoints fo
# Group d'endpoints
router = APIRouter(
    prefix="/api/auth",
    tags=["Auth"],
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = os.getenv("ALGORITHM", "")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 10))
UPLOADS_DIR = os.getenv("UPLOADS_DIR", "static")

os.makedirs(UPLOADS_DIR, exist_ok=True)

# Endpoint pour recuperer touts les utilsateur(pas important voir l'ensemble des utilisateurs)


@router.get("/users")
def get_all_users(session: Session = Depends(get_db)) -> list[UtilisateurBase]:
    print("HelloString")
    return session.query(Utilisateur).all()


@router.post("/login")
async def login(data: UtilisateurLogin, response: Response, session: Session = Depends(get_db)):
    try:
        mot_de_passe = data.mot_de_passe
        email = data.email

        user_authenticated = authenticate_user(email, mot_de_passe, session)
        if not user_authenticated:
            response.status_code = 404
            return {"message": "Identifiants incorrects !"}

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_authenticated.email}, expires_delta=access_token_expires
        )

        # response.set_cookie(key="token", value=access_token,
        #                     expires=3600, max_age=access_token_expires, path="/", samesite="lax")

        return {'status': True, "message": "Utilsateur connecté avec success.", "token": access_token}
    except Exception as e:
        print("ErrorLogin", e)
        response.status_code = 500
        return {'status': False, "message": "Erreur de connexion", "error": str(e)}


@router.post("/forgot-password")
async def forgot_password(response: Response, data: UtilisateurForgotPassword, session: Session = Depends(get_db)):
    try:
        email = data.email
        user = get_user(email, session)
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

        template = env.get_template("./email/reset_password_email.html")
        content = template.render(link=link)

        msg = make_message(
            "Code de verification", content, to=email)
        email_infos = send_email(msg, email,)

        return {'status': True, "token": token, "email_infos": email_infos, "link": link}

    except HTTPException as e:
        response.status_code = e.status_code
        return {"detail": e.detail}
    except Exception as e:
        response.status_code = 500
        return {'status': False, "error_message": str(e)}


@router.post("/reset-password/{token}")
async def reset_password(token: str, reponse: Response, data: UtilisateurReset, session: Session = Depends(get_db)):

    try:
        payload = verify_jwt(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        code_otp = payload.get("code_otp", "")

        user = session.query(Utilisateur).filter(
            Utilisateur.code_otp == code_otp).first()

        if not user:
            raise HTTPException(detail="User not found", status_code=404)

        new_password = data.new_password

        user.mot_de_passe = get_password_hash(new_password)
        user.code_otp = None
        user.code_otp_expiration = None
        session.add(user)
        session.commit()
        session.refresh(user)
        return {"status": True, "user": user}
    except Exception as e:
        reponse.status_code = 500
        return {"status": False, "error": str(e)}


@router.post("/update-password/")
async def update_password(request: Request, response: Response, data: UtilisateurUpdatePassword, session: Session = Depends(get_db)):

    try:
        token = get_auth_token_in_request(request)

        user = get_user_from_session(session, token)

        if not verify_password(data.mot_de_passe_actuel, user.mot_de_passe):
            raise Exception(
                "Mot de passe actuel et mot de passe recu correspoondent pas !")

        user.mot_de_passe = get_password_hash(data.nouveau_de_passe)
        session.add(user)
        session.commit()
        session.refresh(user)

        return {'status': True, "user": user}
    except Exception as e:
        print(e)
        response.status_code = 500
        return {'status': False, "error": str(e)}


@router.post("/is-authenticated/")
def is_authenticated(request: Request, session: Session = Depends(get_db)) -> AuthenticationResult:
    # autoken = request.cookies
    token = get_auth_token_in_request(request)
    user = None
    try:
        user = get_user_from_session(session, token)
    except:
        return {"is_authenticated": False, "user": user}

    if user.photo_profile and not user.photo_profile.startswith(("http://", "https://")):
        user.photo_profile = urljoin(str(request.base_url), user.photo_profile)
    return {"is_authenticated": True, "user": user}


@router.get("/validate-email")
def validate_email(token: str | None, request: Request, session: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, message="Token is required")
    payload = verify_jwt(token)
    email = payload.get('user_email', "")
    user = get_user(email, session)
    user.email_verified = True
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"status": True}


@router.post("/register")
async def register(
    response: Response,
    requests: Request,
    nom_famille: Annotated[str, Form()],
    numero_telephone: Annotated[str, Form()],
    prenom: Annotated[str, Form()],
    email: Annotated[EmailStr, Form()],
    mot_de_passe: Annotated[str, Form()],
    photo_profile: Annotated[UploadFile | str, File(
        description="A file read as UploadFile")] = "",
        session: Session = Depends(get_db)
):
    try:

        image_created_url = None
        if not isinstance(photo_profile, str) and not photo_profile.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400, detail=f"Le fichier {photo_profile.filename} n'est pas une image")
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

        access_token_expires = timedelta(hours=24)
        token = create_access_token(
            data={"user_email": email}, expires_delta=access_token_expires)

        link = os.getenv('APP_URL', "") + "/auth/validate-account?token="+token
        template = env.get_template("./email/register_message.html")
        content = template.render(link=link, prenom=prenom)

        msg = make_message(
            "Votre compte a été crée avec succès.", content, to=email)
        email_result = send_email(msg, email,)

        return {"message": "Utilisateur créé avec success.", "token": token, "email": email_result}
    except HTTPException as e:
        response.status_code = e.status_code
        return e

    except IntegrityError as e:
        response.status_code = 400
        return {"error": "Cet email ou ce numéro de téléphone existe déjà!"}
    except Exception as e:
        response.status_code = 500
        print("Error", e)
        return {"error": str(e)}
    finally:
        session.rollback()


@router.post("/update-profile/")
async def update_profile(
    request: Request,
    response: Response,
    nom_famille: Annotated[str, Form()],
    numero_telephone: Annotated[str, Form()],
    prenom: Annotated[str, Form()],
    # email: Annotated[EmailStr, Form()],
    # mot_de_passe: Annotated[str, Form()],
    photo_profile: Annotated[UploadFile | str, File(
        description="A file read as UploadFile")] = "",
        session: Session = Depends(get_db)
):
    try:
        token = get_auth_token_in_request(request)
        user_connected = get_user_from_session(session, token)
        image_created_url = None
        if photo_profile and not isinstance(photo_profile, str):
            try:
                image_created_url = create_image_file(photo_profile)
            except Exception as e:
                image_created_url = user_connected.photo_profile
        else:
            image_created_url = user_connected.photo_profile

        validate_phone_number(numero_telephone)

        # user_connected.mot_de_passe = get_password_hash(mot_de_passe)
        # user_connected.email = email
        # send_email(user_connected)

        user_connected.nom_famille = nom_famille
        user_connected.prenom = prenom
        user_connected.numero_telephone = numero_telephone
        user_connected.photo_profile = image_created_url

        session.commit()
        session.add(user_connected)
        session.refresh(user_connected)

        APP_URL = os.getenv('APP_URL', "") + "/auth/login"
        template = env.get_template("./email/update_email.html")
        content = template.render(link=APP_URL)
        # msg = make_message(
        #     "Votre compte a été crée avec succès.", content, to=email)
        # email_result = send_email(msg, email,)

        return {"message": "Utilisateur modifié avec success.", "status": True}
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
def delete_user(email: str, session: Session = Depends(get_db)):
    user = get_user(email, session)
    session.delete(user)
    session.commit()
    return {"success": True}


@router.get("/sendemail")
def sendemail(email: str):
    template = env.get_template("./email/test.html")
    content = template.render(link="https://accounts.google.com/")
    msg = make_message(
        "Votre compte a été crée avec succès.", content, to=email)
    email = send_email(msg, to_addrs=email)
    return email