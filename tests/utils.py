from tests.constantes import DATA_STORED, user_mock


def is_authenticated(client):
    response_login = client.post(
        "/api/auth/login", json={"email": user_mock["email"], "mot_de_passe": user_mock["mot_de_passe"]})
    result_login = response_login.json()

    assert response_login.status_code == 200
    assert "token" in result_login
    DATA_STORED["auth_token"] = ["token"]
    assert result_login["status"] is True
