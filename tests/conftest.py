# conftest.py
import pytest
from sqlmodel import SQLModel, Session, create_engine
from fastapi.testclient import TestClient
from app.models import create_db_and_tables
from app.security import create_access_token

from main import app
from app.models import get_db_session
from settings import settings


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        f"postgresql://{settings.postgres_user}:{settings.postgres_password}@"
        f"{settings.postgres_host}:"
        f"{settings.postgres_port}/{settings.postgres_test_db}",
        echo=True,
    )
    create_db_and_tables(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(session):
    def get_session_override():
        return session

    app.dependency_overrides[get_db_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def valid_auth_header():
    token = create_access_token("testuser")
    yield {"Authorization": f"Bearer {token}"}
