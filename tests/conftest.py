import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import app
from core.dbconfig import Base, get_db

sqlite_file_name = "db_test.db"
test_db_url = f"sqlite:///{sqlite_file_name}"


@pytest.fixture(scope="function")
def db_session():
    test_engine = create_engine(test_db_url, echo=True)

    Base.metadata.create_all(bind=test_engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()

    yield session

    session.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    return TestClient(app)


# A revoir
def pytest_collection_modifyitems(items):
    """test items come to last"""
    run_last = ["tests.test_register", "tests.test_c", "tests.test_a"]
    modules = {item: item.module.__name__ for item in items}
    items[:] = sorted(
        items, key=lambda x: run_last.index(
            modules[x]) if modules[x] in run_last else -1
    )
