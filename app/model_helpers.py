from typing import Any

from fastapi import Depends
from sqlmodel import Session, select

from app.models import Feed, get_db_session
from app.schemas import FeedIn


def get_or_create_feed(
    parser: Any,
    feed_in: FeedIn,
    db_session: Session = Depends(get_db_session),
) -> Feed:
    statement = select(Feed).where(Feed.feed_url == str(feed_in.feed_url))
    results = db_session.exec(statement)
    feed = results.first()

    if feed:
        return feed

    feed = Feed(
        feed_url=str(feed_in.feed_url),
        feed_title=parser.feed.title,
        feed_description=parser.feed.description,
    )
    db_session.add(feed)
    db_session.commit()
    db_session.refresh(feed)

    return feed
