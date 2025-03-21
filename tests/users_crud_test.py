# def test_get_users_empty(client):
from features.auth.models import Utilisateur
from datetime import datetime
import os
import uuid
import logging
from tests.constantes import user_mock, DATA_STORED, NEW_PASSWORD, new_user_mock
from features.auth.logic import is_authenticated


def test_register(client, db_session):
    assert len(db_session.query(Utilisateur).all()) == 0
    response = client.post("/api/auth/register", data=user_mock)
    if response.status_code != 200:
        logging.error(f"Response Status Code: {response.status_code}")
        logging.error(f"Response Error Message: {response.text}")
    assert response.status_code == 200
    result = response.json()
    assert "email" in result
    assert result["email"]["is_sent"] == True
    assert len(db_session.query(Utilisateur).all()) == 1

    assert "token" in response.json()
    response_1 = client.get(
        "/api/auth/validate-email?token=" + result["token"],)

    assert response_1.status_code == 200
    assert response_1.json()["status"] is True


def test_login(client, db_session):

    assert len(db_session.query(Utilisateur).all()) == 1

    # is_authenticated(client)
    response_login = client.post(
        "/api/auth/login", json={"email": user_mock["email"], "mot_de_passe": user_mock["mot_de_passe"]})
    result_login = response_login.json()

    assert response_login.status_code == 200
    assert "token" in result_login
    DATA_STORED["auth_token"] = result_login["token"]
    assert result_login["status"] is True


def test_update_password(client, db_session):

    assert len(db_session.query(Utilisateur).all()) == 1

    response = client.post(
        "/api/auth/update-password/", json={"nouveau_de_passe": NEW_PASSWORD, "mot_de_passe_actuel": user_mock["mot_de_passe"]}, headers={"authorization": "Bearer "+DATA_STORED.get("auth_token", "")})

    assert response.status_code == 200
    assert response.json()["status"] is True


def test_update_profile(client, db_session):

    assert len(db_session.query(Utilisateur).all()) == 1

    response = client.post(
        "/api/auth/update-profile/",
        data=new_user_mock,
        headers={"authorization": "Bearer "+DATA_STORED["auth_token"]}
    )

    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] is True
    assert "message" in response.json()


def test_forgot_password(client, db_session):

    response = client.post(
        "/api/auth/forgot-password/",
        json={"email": user_mock["email"]},
    )

    result = response.json()

    assert response.status_code == 200
    assert "status" in result
    assert "email_infos" in result
    assert result["email_infos"]["is_sent"] == True
    assert "token" in result
    assert result["status"] is True

    DATA_STORED["reset_password_token"] = result["token"]


def test_reset_password(client, db_session):

    response = client.post(
        f"/api/auth/reset-password/{DATA_STORED['reset_password_token']}",
        json={"new_password": new_user_mock["mot_de_passe"]},
    )

    result = response.json()

    assert response.status_code == 200
    assert "status" in result
    assert result["status"] is True


def test_create_activity(client, db_session):
    with open("fruit.png", "rb") as f:
        files = [("files", ("fruit.png", f, "image/png"))]
        response = client.post(
            "/api/activities/create-activity/",
            headers={"authorization": "Bearer " + DATA_STORED["auth_token"]},
            files=files
        )
    result_creating = response.json()
    assert response.status_code == 201
    assert "result_data" in result_creating
    assert "global_result" in result_creating
    assert "images" in result_creating


def test_get_activities(client, db_session):

    response = client.get(
        "/api/activities/activities/",
        headers={"authorization": "Bearer " + DATA_STORED["auth_token"]},
    )

    result = response.json()
    assert response.status_code == 200
    assert "stats" in result
    assert "histories" in result
    assert result["stats"]["total_images"] == 1
