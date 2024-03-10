from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select
import feedparser

from app.models import (
    Feed,
    FeedSubscription,
    User,
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
    db_session: Session,
) -> FeedSubscription:
    statement = select(Feed).where(Feed.id == feed_id)
    results = db_session.exec(statement)
    feed = results.first()

    if not feed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feed not found.",
        )

    subscription = FeedSubscription(
        user_id=user.id,
        feed_id=feed.id,
    )
    db_session.add(subscription)
    db_session.commit()
    db_session.refresh(subscription)

    return subscription


"""
async def update_feed_for_subscription(
    feed_subscription: FeedSubscription,
    db_session: Session = Depends(get_db_session),
):
    parser = feedparser.parse(feed_subscription.feed.feed_url)
    for entry in parser.entries:
        statement = select(FeedSubscriptionItem).where(
            FeedSubscriptionItem.guid == entry.guid
        )
        results = db_session.exec(statement)
        existing_item = results.first()
        if existing_item:
            continue

        feed_subscription_item = FeedSubscriptionItem(
            feed_subscription=feed_subscription,
            description=entry.description,
            summary=entry.summary,
            author=entry.author,
            title=entry.title,
            link=entry.link,
            guid=entry.guid,
            publish_date=entry.published_parsed,
        )
        db_session.add(feed_subscription_item)
    db_session.commit()


async def update_feed_for_user(
    user: User,
    db_session: Session = Depends(get_db_session),
):
    tasks = [
        update_feed_for_subscription(feed_subscription, db_session)
        for feed_subscription in user.subscribed_feeds
    ]
    await asyncio.gather(*tasks)
"""
