import feedparser
from pydantic_core import Url
from sqlmodel import select
from app.models import Feed, FeedSubscription, User

from app.utils import DictToObject
from tests.mock_data import (
    sample_parser_response_fail,
    sample_parser_raw_data,
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
    parsed_object = feedparser.parse(sample_parser_raw_data)
    mocked_parser = mocker.patch(
        "app.model_helpers.feedparser.parse",
        return_value=parsed_object,
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


def test_get_feeds_empty_list(client, valid_auth_header):
    response = client.get(
        "/feed",
        headers=valid_auth_header,
    )
    assert response.status_code == 200
    json_list = response.json()
    assert len(json_list) == 0


def test_get_feeds(client, session, valid_auth_header):
    feed = Feed(
        feed_url="https://example.com/feed",
        feed_title="Example Feed",
        feed_description="An example feed",
    )
    session.add(feed)
    session.commit()
    session.refresh(feed)

    response = client.get(
        "/feed",
        headers=valid_auth_header,
    )
    assert response.status_code == 200
    json_list = response.json()
    assert len(json_list) == 1
    assert json_list[0]["feed_url"] == feed.feed_url
    assert json_list[0]["feed_title"] == feed.feed_title
    assert json_list[0]["feed_description"] == feed.feed_description


def test_get_feed_with_id_fails(client, valid_auth_header):
    response = client.get(
        "/feed/1",
        headers=valid_auth_header,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Feed not found."


def test_get_feed_with_id(client, session, valid_auth_header):
    feed = Feed(
        feed_url="https://example.com/feed",
        feed_title="Example Feed",
        feed_description="An example feed",
    )
    session.add(feed)
    session.commit()
    session.refresh(feed)

    response = client.get(
        f"/feed/{feed.id}",
        headers=valid_auth_header,
    )
    assert response.status_code == 200
    json_dict = response.json()
    assert json_dict["feed_url"] == feed.feed_url
    assert json_dict["feed_title"] == feed.feed_title
    assert json_dict["feed_description"] == feed.feed_description


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


def test_create_feed_subscription_already_exists(
    client,
    session,
    test_user: User,
    test_feed: Feed,
    valid_auth_header,
):
    subscription = FeedSubscription(
        user_id=test_user.id,
        feed_id=test_feed.id,
    )
    session.add(subscription)
    session.commit()
    session.refresh(subscription)

    response = client.post(
        f"/feed/{test_feed.id}/subscribe",
        headers=valid_auth_header,
        json={},
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Subscription already exists."


def test_unsubscribe_from_feed(
    client,
    session,
    test_user: User,
    test_feed: Feed,
    valid_auth_header,
):
    subscription = FeedSubscription(
        user_id=test_user.id,
        feed_id=test_feed.id,
    )
    session.add(subscription)
    session.commit()
    session.refresh(subscription)

    response = client.delete(
        f"/feed/{test_feed.id}/unsubscribe",
        headers=valid_auth_header,
    )
    assert response.status_code == 204

    statement = select(FeedSubscription).where(
        FeedSubscription.user_id == test_user.id,
        FeedSubscription.feed_id == test_feed.id,
    )
    results = session.exec(statement)
    subscription = results.first()
    assert subscription is None


def test_unsubscribe_from_feed_not_found(
    client,
    test_feed: Feed,
    valid_auth_header,
):
    response = client.delete(
        f"/feed/{test_feed.id}/unsubscribe",
        headers=valid_auth_header,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Subscription not found."


def test_get_user_feed_entries(
    client,
    test_user: User,
    valid_auth_header,
    set_up_feed,
):
    feed = set_up_feed[0]

    response = client.get(
        "/me/feed-entries",
        headers=valid_auth_header,
    )
    assert response.status_code == 200
    json_list = response.json()
    assert len(json_list) == 2

    for entry in json_list:
        assert entry["feed_id"] == feed.id
        assert entry["title"] is not None
        assert entry["publish_date"] is not None
        assert entry["summary"] is not None
        assert entry["is_read"] is False


def test_mark_feed_entry_as_read(
    client,
    test_user: User,
    valid_auth_header,
    set_up_feed,
    session,
):
    subscription = set_up_feed[2]
    user_entry = subscription.user_feed_entries[0]

    assert user_entry.is_read is False

    response = client.post(
        f"/me/feed-entries/{user_entry.id}/read",
        headers=valid_auth_header,
    )
    assert response.status_code == 200
    json_dict = response.json()
    assert json_dict["is_read"] is True

    session.refresh(user_entry)
    assert user_entry.is_read is True


def test_mark_feed_entry_as_unread(
    client,
    test_user: User,
    valid_auth_header,
    set_up_feed,
    session,
):
    subscription = set_up_feed[2]
    user_entry = subscription.user_feed_entries[0]
    user_entry.is_read = True
    session.commit()

    response = client.post(
        f"/me/feed-entries/{user_entry.id}/unread",
        headers=valid_auth_header,
    )
    assert response.status_code == 200
    json_dict = response.json()
    assert json_dict["is_read"] is False

    session.refresh(user_entry)
    assert user_entry.is_read is False


def test_get_user_feed_entry(
    client,
    test_user: User,
    valid_auth_header,
    set_up_feed,
):
    user_entry = set_up_feed[2].user_feed_entries[0]

    response = client.get(
        f"/me/feed-entries/{user_entry.id}",
        headers=valid_auth_header,
    )
    assert response.status_code == 200
    json_dict = response.json()
    assert json_dict["id"] == user_entry.id
    assert json_dict["feed_id"] == user_entry.feed_entry.feed_id
    assert json_dict["title"] == user_entry.feed_entry.title
    assert json_dict["summary"] == user_entry.feed_entry.summary
    assert json_dict["is_read"] == user_entry.is_read


def test_refresh_user_feed_entries(
    client,
    test_user: User,
    valid_auth_header,
    set_up_feed,
    mocker,
):
    mocker.patch(
        "app.model_helpers.feedparser.parse",
        return_value=feedparser.parse(sample_parser_raw_data),
    )

    response = client.post(
        "/me/feed-entries/refresh",
        headers=valid_auth_header,
    )
    assert response.status_code == 200
