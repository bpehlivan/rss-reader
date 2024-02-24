from typing import Optional, List
from datetime import datetime

import validators
from pydantic import field_validator
from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    # It is Optional due to typing, Not optional inside DB
    id: Optional[int] = Field(default=None, primary_key=True)
    subscribed_feeds: List["FeedSubscription"] = Relationship(
        back_populates="user"
    )
    password: str
    email: str
    full_name: str


class Feed(SQLModel, table=True):
    items: List["FeedItem"] = Relationship(back_populates="feed")
    feed_url: str
    feed_title: str
    feed_description: str

    @field_validator("feed_url")
    @classmethod
    def feed_url_validator(cls, value: str) -> str:
        if not validators.url(value):
            raise ValueError("Given value is not a valid URL.")
        return value


class FeedSubscription(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user: User = Relationship(back_populates="subscribed_feeds")
    user_id: int = Field(default=None, foreign_key="user.id")
    feed: "Feed" = Relationship(back_populates="subscribed_users")
    feed_id: int = Field(default=None, foreign_key="feed.id")


class FeedItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    feed_subscription_id: int = Field(
        default=None,
        foreign_key="feed.id",
    )
    feed_subscription: "Feed" = Relationship(
        back_populates="items",
    )
    is_read: bool = False
    title: str
    link: str
    description: str
    guid: str
    pub_date: datetime
