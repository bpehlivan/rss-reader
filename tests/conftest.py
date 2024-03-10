# conftest.py
from typing import Generator
import pytest
from sqlalchemy import Engine
from sqlmodel import SQLModel, Session, create_engine
from fastapi.testclient import TestClient
from app.models import Feed, User, create_db_and_tables
from app.security import create_access_token

from main import app
from app.models import get_db_session
from settings import settings


@pytest.fixture(scope="session")
def engine() -> Generator[Engine, None, None]:
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
def session(engine: Engine) -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(session: Session) -> Generator[TestClient, None, None]:
    def get_session_override():
        return session

    app.dependency_overrides[get_db_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(session: Session) -> Generator[User, None, None]:
    user = User(
        username="testuser",
        password="securepassword",
        full_name="Test User",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    yield user


@pytest.fixture(scope="function")
def valid_auth_header(test_user: User) -> Generator[str, str, None]:
    token = create_access_token(test_user.username)
    yield {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def test_feed(session: Session) -> Generator[Feed, None, None]:
    feed = Feed(
        feed_url="https://testfeed.com/rss",
        feed_title="Test Feed",
    )
    session.add(feed)
    session.commit()
    session.refresh(feed)
    yield feed
