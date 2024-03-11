from typing import Optional, List
from datetime import datetime
from sqlalchemy import Column, DateTime, func

import validators
from pydantic import field_validator
from sqlmodel import (
    SQLModel,
    Field,
    Relationship,
    Session,
    create_engine,
    UniqueConstraint,
)

from settings import settings

engine = create_engine(
    f"postgresql://{settings.postgres_user}:{settings.postgres_password}@"
    f"{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
)


def get_db_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables(engine=engine):
    SQLModel.metadata.create_all(engine)


class User(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("username"),)
    # It is Optional due to typing, Not optional inside DB
    id: Optional[int] = Field(default=None, primary_key=True)

    subscribed_feeds: List["FeedSubscription"] = Relationship(
        back_populates="user"
    )

    is_active: bool = True
    username: str
    password: str
    full_name: str


class Feed(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("feed_url"),)
    id: Optional[int] = Field(default=None, primary_key=True)
    feed_entries: List["FeedEntry"] = Relationship(
        back_populates="feed",
    )
    feed_subscriptions: List["FeedSubscription"] = Relationship(
        back_populates="feed",
    )

    feed_description: Optional[str] = None
    is_active: bool = True
    feed_url: str
    feed_title: str

    @field_validator("feed_url")
    @classmethod
    def feed_url_validator(cls, value: str) -> str:
        if not validators.url(value):
            raise ValueError("Given value is not a valid URL.")
        return value


class FeedEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    feed: Feed = Relationship(back_populates="feed_entries")
    feed_id: int = Field(default=None, foreign_key="feed.id")

    description: Optional[str] = None
    summary: Optional[str] = None
    author: Optional[str] = None
    publish_date: Optional[datetime] = None
    title: str
    link: str
    guid: str


class FeedSubscription(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    user: User = Relationship(back_populates="subscribed_feeds")
    user_id: int = Field(default=None, foreign_key="user.id")

    feed: "Feed" = Relationship(back_populates="feed_subscriptions")
    feed_id: int = Field(default=None, foreign_key="feed.id")

    user_feed_entries: List["UserFeedEntry"] = Relationship(
        back_populates="subscription",
    )

    # see:
    # https://github.com/tiangolo/sqlmodel/issues/370#issuecomment-1169674418
    created_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )


class UserFeedEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    subscription: FeedSubscription = Relationship(
        back_populates="user_feed_entries",
    )
    subscription_id: int = Field(
        default=None,
        foreign_key="feedsubscription.id",
    )

    feed_entry: FeedEntry = Relationship(back_populates=None)
    feed_entry_id: int = Field(default=None, foreign_key="feedentry.id")

    created_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )

    is_read: bool = False
    is_favorite: bool = False
    is_archived: bool = False
