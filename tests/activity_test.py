from features.auth.models import Utilisateur
import pytest
from tests.constantes import user_mock, DATA_STORED, NEW_PASSWORD, new_user_mock
from features.auth.logic import is_authenticated


# @pytest.mark.dependency(depends=['test_register'])
def create_activity(client, db_session):

    # assert len(db_session.query(Utilisateur).all()) == 1

    # Se loogger
    is_authenticated(client)
