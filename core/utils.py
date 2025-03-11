import os
from dotenv import load_dotenv
from fastapi import HTTPException
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re
from datetime import datetime
from core.lib.session import session
import jwt
import random
from features.auth.models import Utilisateur

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = os.getenv("ALGORITHM", "")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 10))


def make_message(subject: str, content: str, to: str,) -> MIMEMultipart:
    _from = os.getenv("SMTP_SERVER_ADDR", "")
    msg = MIMEMultipart()
    msg["To"] = to
    msg["From"] = _from
    msg["Subject"] = subject
    part2 = MIMEText(content, 'html')
    msg.attach(part2)
    return msg


def send_email(msg: MIMEMultipart, to_addrs: str) -> bool:
    port: int = int(os.getenv('PORT_SMTP', 587))
    from_addr: str = os.getenv("SMTP_SERVER_ADDR", "")
    host: str = os.getenv("SMTP_HOST", "")
    passowrd = os.getenv("SMTP_PASSWORD", "")
    try:
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(from_addr, passowrd)
            server.sendmail(from_addr, to_addrs, msg.as_string())
        return {"to": to_addrs, "is_sent": True}
    except Exception as e:
        print("Error mail sending", e)
        return {"to": to_addrs, "is_sent": False, "error_message": str(e)}


def generate_otp_code(nb: int = 6) -> str:
    code = [str(random.randint(0, 9)) for _ in range(0, nb)]
    return "".join(code)


def validate_phone_number(phone_number):
    phone_regex = r'^\+?\d{1,4}[-\s]?\(?\d{1,4}\)?[-\s]?\d{6,15}$'
    if re.match(phone_regex, phone_number):
        return phone_number
    raise HTTPException(detail="Numéro de tel invalid", status_code=500)


def get_user(email: str):
    return session.query(Utilisateur).filter(
        Utilisateur.email == email).first()


def get_user_from_session(token):
    if not token:
        raise Exception("Vous n'êtes pas connecté!")

    payload_jwt_decoded = jwt.decode(
        token, key=SECRET_KEY, algorithms=[ALGORITHM])

    current_time = datetime.utcnow()
    expiration_time = datetime.utcfromtimestamp(payload_jwt_decoded["exp"])

    if expiration_time < current_time:
        raise HTTPException(detail="Le token a expiré!", status_code=401)

    if not payload_jwt_decoded:
        raise HTTPException(detail="Token invalide!", status_code=401)

    user = get_user(payload_jwt_decoded["sub"])
    if not user:
        raise HTTPException(
            status_code=404, detail="Aucun utilisateeur trouvé !")
    return user
