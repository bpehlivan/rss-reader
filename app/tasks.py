from celery import Celery, Task
from celery.schedules import crontab
from sqlmodel import Session, select
from app.model_helpers import update_entries_for_feed

from settings import settings
from app.models import Feed, FeedSubscription, User, engine


celery_app = Celery(
    __name__,
    broker=settings.redis_host,
    backend=settings.redis_host,
    include=["app.tasks"],
)


celery_app.conf.beat_schedule = {
    'update_all_user_subscriptions_every_5_minutes': {
        'task': 'app.tasks.update_all_user_subscriptions',
        'schedule': crontab(minute='*/5'),
    },
    'update_all_feeds_every_5_minutes': {
        'task': 'app.tasks.update_all_feeds',
        'schedule': crontab(minute='*/5'),
    },
}


class BaseTaskWithRetry(Task):
    autoretry_for = (Exception,)
    retry_backoff = True
    retry_backoff_max = 600
    retry_jitter = True
    max_retries = 3


@celery_app.task(base=BaseTaskWithRetry)
def update_entries_for_feed_task(feed_id: int):
    with Session(engine) as session:
        statement = select(Feed).where(Feed.id == feed_id)
        results = session.exec(statement)
        feed = results.first()

        if feed:
            update_entries_for_feed(
                feed=feed,
                db_session=session,
                mark_subscriptions_for_update=True,
            )


# subtask
@celery_app.task(base=BaseTaskWithRetry)
def update_subscription_task(feed_subscription_id: int):

    with Session(engine) as session:
        statement = select(FeedSubscription).where(
            FeedSubscription.id == feed_subscription_id,
        )
        results = session.exec(statement)
        subscription = results.first()

        if subscription:
            update_entries_for_feed(
                feed=subscription,
                db_session=session,
                mark_subscriptions_for_update=True,
            )


# subtask
@celery_app.task(base=BaseTaskWithRetry)
def update_subscriptions_of_a_user(user_id: int):
    with Session(engine) as session:
        statement = select(FeedSubscription).where(
            FeedSubscription.user_id == user_id,
        )
        results = session.exec(statement)
        subscriptions = results.all()

        for subscription in subscriptions:
            update_subscription_task.delay(subscription.id)


# periodic task
@celery_app.task(base=BaseTaskWithRetry)
def update_all_user_subscriptions():
    with Session(engine) as session:
        statement = select(User).where(User.is_active == True)  # noqa
        results = session.exec(statement)
        all_users = results.all()

        for user in all_users:
            update_subscriptions_of_a_user.delay(user.id)


# periodic task
@celery_app.task(base=BaseTaskWithRetry)
def update_all_feeds():
    with Session(engine) as session:
        statement = select(Feed).where(Feed.is_active == True)  # noqa
        results = session.exec(statement)
        feeds = results.all()

        for feed in feeds:
            update_entries_for_feed_task.delay(feed.id)
