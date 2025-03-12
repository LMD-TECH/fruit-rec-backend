from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional


class UtilisateurBase(BaseModel):
    nom_famille: str
    photo_profile: str | None
    prenom: str
    email: EmailStr
    numero_telephone: str
    email_verified: bool


class UtilisateurCreate(UtilisateurBase):
    mot_de_passe: str


class UtilisateurLogin(BaseModel):
    email: EmailStr
    mot_de_passe: str


class UtilisateurForgotPassword(BaseModel):
    email: EmailStr = "mallemoussa091@gmail.com"


class AuthenticationResult(BaseModel):
    is_authenticated: bool
    user: UtilisateurBase | None


class UtilisateurReset(BaseModel):
    new_password: str


class UtilisateurUpdatePassword(BaseModel):
    mot_de_passe_actuel: str
    nouveau_de_passe: str


class UtilisateurResponse(UtilisateurBase):
    id_utilisateur: int
    date_creation_compte: datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None
