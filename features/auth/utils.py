from passlib.context import CryptContext

from datetime import datetime
from core.utils import get_user
from .models import Utilisateur
from datetime import datetime, timezone, timedelta
import os
from dotenv import load_dotenv
import jwt

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = os.getenv("ALGORITHM", "")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 10))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None, SECRET_KEY=SECRET_KEY, ALGORITHM=ALGORITHM):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_jwt(token, key=SECRET_KEY, algorithms=ALGORITHM):
    return jwt.decode(token, algorithms=algorithms, key=key)


def authenticate_user(email: str, mot_de_passe: str):
    user = get_user(email)
    if not user:
        return False
    if not user.email_verified:
        return False

    mot_de_passe_correspond = verify_password(mot_de_passe, user.mot_de_passe)
    if not mot_de_passe_correspond:
        return False

    return user
