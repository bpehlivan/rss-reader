from pydantic import BaseModel, ConfigDict, Field


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
    feed_url: str
