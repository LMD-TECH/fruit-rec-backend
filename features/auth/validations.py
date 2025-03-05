from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional


class UtilisateurBase(BaseModel):
    nom_famille: str
    photo_profile: str
    prenom: str
    email: EmailStr
    numero_telephone: str


class UtilisateurCreate(UtilisateurBase):
    mot_de_passe: str


class UtilisateurLogin(BaseModel):
    email: EmailStr
    mot_de_passe: str


class UtilisateurReset(BaseModel):
    email: EmailStr


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
