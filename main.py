from typing import Annotated

import feedparser
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.models import (
    Feed,
    FeedSubscription,
    User,
    create_db_and_tables,
    get_db_session,
)
from app.model_helpers import get_or_create_feed
from app.schemas import FeedIn, FeedOut, Token, UserIn, UserOut
from app.security import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    hash_password,
)


def lifespan(app: FastAPI):
    """
    Create the database and tables when the app starts
    """
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/register", response_model=UserOut, status_code=201)
def register_user(
    user_in: UserIn,
    db_session: Session = Depends(get_db_session),
) -> UserOut:
    statement = select(User).where(User.username == user_in.username)
    results = db_session.exec(statement)
    existing_user = results.first()

    if existing_user:
        raise HTTPException(
            detail="User with the same username already exists",
            status_code=400,
        )

    hashed_password = hash_password(user_in.password)
    user = User(
        username=user_in.username,
        full_name=user_in.full_name,
        password=hashed_password,
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return UserOut.model_validate(user)


@app.post("/login")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db_session: Session = Depends(get_db_session),
) -> Token:
    user: User | None = authenticate_user(
        db_session,
        form_data.username,
        form_data.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(username=user.username)
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/", response_model=UserOut)
def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return UserOut.model_validate(current_user)


@app.post("/feed/subscribe", response_model=FeedOut, status_code=201)
def subscribe_to_feed(
    feed_in: FeedIn,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db_session: Session = Depends(get_db_session),
) -> FeedOut:
    parser = feedparser.parse(str(feed_in.feed_url))

    if parser.bozo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something is wrong with the feed",
        )

    feed: Feed = get_or_create_feed(parser, feed_in, db_session)

    subscription = FeedSubscription(
        user_id=current_user.id,
        feed_id=feed.id,
    )
    db_session.add(subscription)
    db_session.commit()
    db_session.refresh(subscription)

    return FeedOut.model_validate(feed)
