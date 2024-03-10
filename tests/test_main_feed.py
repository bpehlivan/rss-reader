from pydantic_core import Url
from sqlmodel import select
from app.models import Feed, FeedSubscription, User

from app.utils import DictToObject
from tests.mock_data import (
    sample_parser_response_fail,
    sample_parser_response_success,
)


def test_create_feed_not_authorized(client):
    response = client.post(
        "/feed",
        json={
            "feed_url": "https://example.com/feed",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_create_feed_fail(client, valid_auth_header, mocker):
    mocked_parser = mocker.patch(
        "app.model_helpers.feedparser.parse",
        return_value=DictToObject(sample_parser_response_fail),
    )

    test_url = "https://example.com/feed"
    response = client.post(
        "/feed",
        headers=valid_auth_header,
        json={"feed_url": test_url},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Something is wrong with the feed"

    mocked_parser.assert_called_once_with(Url(test_url))


def test_create_feed_success(client, session, valid_auth_header, mocker):
    mocked_parser = mocker.patch(
        "app.model_helpers.feedparser.parse",
        return_value=DictToObject(sample_parser_response_success),
    )

    test_url = "https://example.com/feed"
    response = client.post(
        "/feed",
        headers=valid_auth_header,
        json={"feed_url": test_url},
    )
    assert response.status_code == 201
    json_dict = response.json()

    statement = select(Feed).where(Feed.id == json_dict["id"])
    results = session.exec(statement)
    feed: Feed = results.first()
    assert feed is not None

    assert json_dict["feed_url"] == test_url
    assert json_dict["feed_title"] == feed.feed_title
    assert json_dict["feed_description"] == feed.feed_description

    mocked_parser.assert_called_once_with(Url(test_url))


def test_create_feed_subscription_not_authorized(client):
    response = client.post(
        "/feed/1/subscribe",
        json={},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_create_feed_subscription_feed_not_exists(
    client,
    valid_auth_header,
):
    response = client.post(
        "/feed/1/subscribe",
        headers=valid_auth_header,
        json={},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Feed not found."


def test_create_feed_subscription_success(
    client,
    session,
    test_user: User,
    test_feed: Feed,
    valid_auth_header,
):
    response = client.post(
        f"/feed/{test_feed.id}/subscribe",
        headers=valid_auth_header,
        json={},
    )
    assert response.status_code == 201
    json_dict = response.json()

    statement = select(FeedSubscription).where(
        FeedSubscription.user_id == test_user.id,
    )
    results = session.exec(statement)
    feed_subscription: FeedSubscription = results.first()
    assert feed_subscription is not None

    assert json_dict["user_id"] == test_user.id
    assert json_dict["feed_id"] == test_feed.id
    assert json_dict["id"] == feed_subscription.id
