import feedparser
from sqlmodel import select
from app.model_helpers import (
    update_entries_for_feed,
    update_subscription_entries,
)
from app.models import Feed, FeedEntry, FeedSubscription, UserFeedEntry
from tests.mock_data import sample_parser_raw_data


def test_update_entries_for_feed(session, mocker):
    parsed_object = feedparser.parse(sample_parser_raw_data)

    # Create a mock feed and entries
    feed = Feed(
        feed_url="https://example.com/rss",
        feed_title="Example Feed",
    )

    session.add(feed)
    session.commit()
    session.refresh(feed)

    mocked_parser = mocker.patch(
        "app.model_helpers.feedparser.parse",
        return_value=parsed_object,
    )

    update_entries_for_feed(feed, session)

    mocked_parser.assert_called_once_with(feed.feed_url)

    statement = select(FeedEntry).where(FeedEntry.feed_id == feed.id)
    results = session.exec(statement)
    entries = results.all()

    assert len(entries) == 2
    assert entries[0].feed_id == feed.id
    assert entries[0].title is not None
    assert entries[0].link is not None
    assert entries[0].publish_date is not None
    assert entries[0].summary is not None

    assert entries[1].feed_id == feed.id
    assert entries[1].title is not None
    assert entries[1].link is not None
    assert entries[1].publish_date is not None
    assert entries[1].summary is not None


def test_update_subscription_entries(session, test_user, mocker):
    parsed_object = feedparser.parse(sample_parser_raw_data)

    # Create a mock feed and entries
    feed = Feed(
        feed_url="https://example.com/rss",
        feed_title="Example Feed",
    )

    session.add(feed)
    session.commit()
    session.refresh(feed)

    mocker.patch(
        "app.model_helpers.feedparser.parse",
        return_value=parsed_object,
    )

    update_entries_for_feed(feed, session)

    # Create a feed subscription
    subscription = FeedSubscription(
        user_id=test_user.id,
        feed_id=feed.id,
    )
    session.add(subscription)
    session.commit()
    session.refresh(subscription)

    # Update the subscription
    update_subscription_entries(subscription, session)

    statement = select(UserFeedEntry).where(
        UserFeedEntry.subscription_id == subscription.id,
    )
    results = session.exec(statement)
    user_feed_entries = results.all()

    assert len(user_feed_entries) == 2
    assert user_feed_entries[0].feed_entry_id is not None
    assert user_feed_entries[0].subscription_id == subscription.id
    assert not user_feed_entries[0].is_read

    assert user_feed_entries[1].feed_entry_id is not None
    assert user_feed_entries[1].subscription_id == subscription.id
    assert not user_feed_entries[1].is_read
