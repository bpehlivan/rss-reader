from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.models import (
    Feed,
    FeedSubscription,
    User,
    UserFeedEntry,
    create_db_and_tables,
    get_db_session,
)
from app.model_helpers import (
    create_feed_in_database,
    create_feed_subscription_with_feed_id,
    unscubscribe_from_feed,
    update_entries_for_feed,
    update_subscription_entries,
)
from app.schemas import (
    FeedIn,
    FeedOut,
    Token,
    UserFeedEntryOut,
    UserIn,
    UserOut,
)
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


@app.post("/token")
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


@app.post("/feed", response_model=FeedOut, status_code=201)
def create_feed(
    feed_in: FeedIn,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db_session: Session = Depends(get_db_session),
) -> FeedOut:
    feed: Feed = create_feed_in_database(feed_in, db_session)
    return FeedOut.model_validate(feed)


@app.get("/feed", response_model=list[FeedOut])
def get_feeds(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db_session: Session = Depends(get_db_session),
) -> list[FeedOut]:
    statement = select(Feed)
    results = db_session.exec(statement)
    feeds = results.all()

    return [FeedOut.model_validate(feed) for feed in feeds]


@app.get("/feed/{feed_id}", response_model=FeedOut)
def get_feed(
    feed_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db_session: Session = Depends(get_db_session),
) -> FeedOut:
    statement = select(Feed).where(Feed.id == feed_id)
    results = db_session.exec(statement)
    feed = results.first()

    if not feed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feed not found.",
        )

    return FeedOut.model_validate(feed)


@app.post(
    "/feed/{feed_id}/subscribe",
    response_model=FeedSubscription,
    status_code=201,
)
def subscribe_to_feed(
    feed_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db_session: Session = Depends(get_db_session),
) -> FeedSubscription:
    subscription = create_feed_subscription_with_feed_id(
        feed_id, current_user, db_session
    )

    return subscription


@app.get("me/subscriptions", response_model=list[FeedOut])
def get_subscribed_feeds(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db_session: Session = Depends(get_db_session),
) -> list[FeedOut]:
    statement = select(Feed).join(FeedSubscription).where(
        FeedSubscription.user_id == current_user.id
    )
    results = db_session.exec(statement)
    feeds = results.all()

    return [FeedOut.model_validate(feed) for feed in feeds]


@app.delete(
    "/feed/{feed_id}/unsubscribe",
    status_code=204,
)
def unsubscribe_from_feed(
    feed_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db_session: Session = Depends(get_db_session),
):
    unscubscribe_from_feed(
        feed_id,
        current_user,
        db_session,
    )
    return


@app.get("/me/feed-entries", response_model=list[UserFeedEntryOut])
def get_user_feed_entries(
    current_user: Annotated[User, Depends(get_current_active_user)],
    is_read: bool = False,
    order_by_date_desc: bool = True,
    db_session: Session = Depends(get_db_session),
) -> list[UserFeedEntryOut]:
    statement = select(FeedSubscription).where(
        FeedSubscription.user_id == current_user.id
    )
    results = db_session.exec(statement)
    subscriptions = results.all()

    subscription_ids = [subscription.id for subscription in subscriptions]

    statement = select(UserFeedEntry).where(
        UserFeedEntry.subscription_id.in_(subscription_ids),
        UserFeedEntry.is_read == is_read,
    ).order_by(
        UserFeedEntry.created_at.desc()
        if order_by_date_desc
        else UserFeedEntry.created_at.asc()
    )
    results = db_session.exec(statement)
    user_feed_entries = results.all()

    feed_list = []

    for user_feed_entry in user_feed_entries:
        entry_out = UserFeedEntryOut.model_validate(user_feed_entry.feed_entry)
        entry_out.is_read = user_feed_entry.is_read
        entry_out.id = user_feed_entry.id
        feed_list.append(entry_out)

    return feed_list


@app.get("/me/feed-entries/{user_feed_id}", response_model=UserFeedEntryOut)
def get_user_feed_entry(
    user_feed_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db_session: Session = Depends(get_db_session),
) -> UserFeedEntryOut:
    statement = select(UserFeedEntry).where(
        UserFeedEntry.id == user_feed_id,
    )
    results = db_session.exec(statement)
    user_feed_entry = results.first()

    if not user_feed_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feed entry not found.",
        )

    entry_out = UserFeedEntryOut.model_validate(user_feed_entry.feed_entry)
    entry_out.is_read = user_feed_entry.is_read
    entry_out.id = user_feed_entry.id
    return entry_out


@app.post(
    "/me/feed-entries/{user_feed_id}/read",
    response_model=UserFeedEntryOut,
    status_code=200,
)
def mark_feed_entry_as_read(
    user_feed_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db_session: Session = Depends(get_db_session),
) -> UserFeedEntryOut:
    statement = select(UserFeedEntry).where(
        UserFeedEntry.id == user_feed_id,
    )
    results = db_session.exec(statement)
    user_feed_entry = results.first()

    if not user_feed_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feed entry not found.",
        )

    user_feed_entry.is_read = True
    db_session.commit()
    db_session.refresh(user_feed_entry)

    entry_out = UserFeedEntryOut.model_validate(user_feed_entry.feed_entry)
    entry_out.is_read = user_feed_entry.is_read
    entry_out.id = user_feed_entry.id
    return entry_out


@app.post(
    "/me/feed-entries/{user_feed_id}/unread",
    response_model=UserFeedEntryOut,
    status_code=200,
)
def mark_feed_entry_as_unread(
    user_feed_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db_session: Session = Depends(get_db_session),
) -> UserFeedEntryOut:
    statement = select(UserFeedEntry).where(
        UserFeedEntry.id == user_feed_id,
    )
    results = db_session.exec(statement)
    user_feed_entry = results.first()

    if not user_feed_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feed entry not found.",
        )

    user_feed_entry.is_read = False
    db_session.commit()
    db_session.refresh(user_feed_entry)

    entry_out = UserFeedEntryOut.model_validate(user_feed_entry.feed_entry)
    entry_out.is_read = user_feed_entry.is_read
    entry_out.id = user_feed_entry.id
    return entry_out


@app.post(
    "/me/feed-entries/refresh",
    status_code=200,
)
def refresh_user_feed_entries(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db_session: Session = Depends(get_db_session),
):
    statement = select(FeedSubscription).where(
        FeedSubscription.user_id == current_user.id
    )
    results = db_session.exec(statement)
    subscriptions = results.all()

    for subscription in subscriptions:
        update_entries_for_feed(subscription.feed, db_session)
        update_subscription_entries(subscription, db_session)

    return
