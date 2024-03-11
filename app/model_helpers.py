from datetime import datetime
from time import mktime
from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select
import feedparser

from app.models import (
    Feed,
    FeedEntry,
    FeedSubscription,
    User,
    UserFeedEntry,
    get_db_session,
)
from app.schemas import FeedIn


def create_feed_in_database(
    feed_in: FeedIn,
    db_session: Session = Depends(get_db_session),
) -> Feed:
    statement = select(Feed).where(Feed.feed_url == str(feed_in.feed_url))
    results = db_session.exec(statement)
    feed = results.first()

    if feed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Feed already exists.",
        )

    parser = feedparser.parse(feed_in.feed_url)

    if parser.bozo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something is wrong with the feed",
        )

    feed = Feed(
        feed_url=str(feed_in.feed_url),
        feed_title=parser.feed.title,
        feed_description=parser.feed.description,
    )
    db_session.add(feed)
    db_session.commit()
    db_session.refresh(feed)

    return feed


def create_feed_subscription_with_feed_id(
    feed_id: int,
    user: User,
    db_session: Session = Depends(get_db_session),
) -> FeedSubscription:
    statement = select(Feed).where(Feed.id == feed_id)
    results = db_session.exec(statement)
    feed = results.first()

    if not feed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feed not found.",
        )

    statement = select(FeedSubscription).where(
        FeedSubscription.user_id == user.id,
        FeedSubscription.feed_id == feed.id,
    )
    results = db_session.exec(statement)
    existing_subscription = results.first()

    if existing_subscription:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Subscription already exists.",
        )

    subscription = FeedSubscription(
        user_id=user.id,
        feed_id=feed.id,
    )
    db_session.add(subscription)
    db_session.commit()
    db_session.refresh(subscription)

    return subscription


def unscubscribe_from_feed(
    feed_id: int,
    user: User,
    db_session: Session = Depends(get_db_session),
):
    statement = select(FeedSubscription).where(
        FeedSubscription.user_id == user.id,
        FeedSubscription.feed_id == feed_id,
    )
    results = db_session.exec(statement)
    subscription = results.first()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found.",
        )

    db_session.delete(subscription)
    db_session.commit()


def update_entries_for_feed(
    feed: Feed,
    db_session: Session = Depends(get_db_session),
):
    parser = feedparser.parse(feed.feed_url)

    if parser.bozo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something is wrong with the feed",
        )

    for entry in parser.entries:
        statement = select(FeedEntry).where(
            FeedEntry.guid == entry.id,
        )
        results = db_session.exec(statement)
        existing_entry = results.first()

        if existing_entry:
            continue

        feed_entry = FeedEntry(
            feed_id=feed.id,
            title=entry.title,
            link=entry.link,
            description=entry.description,
            guid=entry.id,
            summary=entry.summary,
            publish_date=datetime.fromtimestamp(
                mktime(entry.published_parsed)
            ),
        )
        db_session.add(feed_entry)
    db_session.commit()


def update_subscription_entries(
    subscription: FeedSubscription,
    db_session: Session = Depends(get_db_session),
):
    """
    This function updates the entries for a specific subscription.
    """

    feed = subscription.feed

    select_entries_statement = select(FeedEntry).where(
        FeedEntry.feed_id == feed.id,
    )
    results = db_session.exec(select_entries_statement)
    entries = results.all()

    for entry in entries:
        user_feed_entry_statement = select(UserFeedEntry).where(
            UserFeedEntry.subscription_id == subscription.id,
            UserFeedEntry.feed_entry_id == entry.id,
        )
        results = db_session.exec(user_feed_entry_statement)
        user_feed_entry = results.first()

        if user_feed_entry:
            continue

        user_feed_entry = UserFeedEntry(
            subscription_id=subscription.id,
            feed_entry_id=entry.id,
            is_read=False,
        )
        db_session.add(user_feed_entry)
        db_session.commit()
