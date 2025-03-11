import os
from dotenv import load_dotenv
from fastapi import HTTPException, Request, status
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re
from datetime import datetime
from core.lib.session import session
import jwt
import random
import requests
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


def send_email(msg: MIMEMultipart, to_addrs: str) -> dict:
    port: int = int(os.getenv('PORT_SMTP', 587))
    from_addr: str = os.getenv("SMTP_SERVER_ADDR", "").strip()
    host: str = os.getenv("SMTP_HOST", "").strip()
    password = os.getenv("SMTP_PASSWORD", "").strip()

    if not all([port, from_addr, host, password]):
        return {"to": to_addrs, "is_sent": False, "error_message": "Missing SMTP configuration"}

    try:
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(from_addr, password)
            server.sendmail(from_addr, to_addrs, msg.as_string())

        return {"to": to_addrs, "is_sent": True}

    except Exception as e:
        print("Error sending email:", e)
        return {"to": to_addrs, "is_sent": False, "error_message": str(e)}


def send_email_v2(msg: MIMEMultipart, to_addrs: str) -> dict:
    maileroo_api_url = "https://smtp.maileroo.com/send"
    contentType = "multipart/form-data"

    try:
        response = requests.post(maileroo_api_url, json={
            "from": "APP Name <fruit-rec-app@0c521d74db3aeeb4.maileroo.org>",
            "to": to_addrs,
            "subject": "Hello test",
            "plain": "Bonjour tout le monde"
        }, headers={
            "Content-Type": contentType, "X-API-Key": "d67ca20aa009f2bf98abe2510f5c87d9477f2bba906ab1c3fb5fbb77f809ee9d"
        })
        return {"to": to_addrs, "is_sent": True, "response": response.json()}

    except Exception as e:
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


def get_auth_token_in_request(request: Request):
    bearer, token = request._headers["authorization"].split(" ")
    if not bearer != "Bearer " or not token:
        raise HTTPException(
            details="Invalid bearer", status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
    return token
