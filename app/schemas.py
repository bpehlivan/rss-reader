from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, AnyUrl


class UserIn(BaseModel):
    username: str = Field(min_length=5, max_length=64)
    password: str = Field(min_length=8, max_length=64)
    full_name: str = Field(min_length=5, max_length=64)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: str
    full_name: str
    id: int


class Token(BaseModel):
    access_token: str
    token_type: str


class FeedIn(BaseModel):
    feed_url: AnyUrl


class FeedOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    feed_description: Optional[str] = None
    feed_url: str
    feed_title: str
    id: int


class UserFeedEntryOut(BaseModel):
    """Merged version of both UserFeedEntry and FeedEntry models"""
    model_config = ConfigDict(from_attributes=True)
    description: Optional[str] = None
    summary: Optional[str] = None
    publish_date: Optional[datetime] = None
    is_read: bool = False
    feed_id: int
    title: str
    id: int
