from typing import Generator

import feedparser
import pytest
from sqlalchemy import Engine
from sqlmodel import SQLModel, Session, create_engine
from fastapi.testclient import TestClient
from app.model_helpers import (
    update_entries_for_feed,
    update_subscription_entries,
)
from app.models import Feed, FeedSubscription, User, create_db_and_tables
from app.security import create_access_token

from main import app
from app.models import get_db_session
from settings import settings
from tests.mock_data import sample_parser_raw_data


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


@pytest.fixture(scope="function")
def set_up_feed(session: Session, test_feed, test_user, mocker):
    parsed_object = feedparser.parse(sample_parser_raw_data)

    mocker.patch(
        "app.model_helpers.feedparser.parse",
        return_value=parsed_object,
    )
    update_entries_for_feed(test_feed, session)
    subscription = FeedSubscription(
        user_id=test_user.id,
        feed_id=test_feed.id,
    )
    session.add(subscription)
    session.commit()
    session.refresh(subscription)

    update_subscription_entries(subscription, session)
    yield test_feed, test_user, subscription
