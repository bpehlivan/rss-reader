from celery import Celery
from sqlmodel import Session, select

from settings import settings
from app.models import User, engine


celery_app = Celery(
    __name__,
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks"],
)


@celery_app.task
def update_feed_for_user(user_id: int):
    with Session(engine) as session:
        statement = select(User).where(User.id == user_id)
        results = session.exec(statement)
        user = results.first()

        update_feed_for_user(user, session)
