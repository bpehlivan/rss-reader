from fastapi import FastAPI, HTTPException
from sqlmodel import Session, select

from app.models import User, create_db_and_tables, engine
from app.schemas import UserIn, UserOut
from app.security import hash_password


def lifespan(app: FastAPI):
    """
    Create the database and tables when the app starts
    """
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/register", response_model=UserOut, status_code=201)
def register_user(user_in: UserIn) -> UserOut:
    with Session(engine) as session:
        statement = select(User).where(User.email == user_in.email)
        results = session.exec(statement)
        existing_user = results.first()

        if existing_user:
            raise HTTPException(
                detail="User with the same email already exists",
                status_code=400,
            )

        hashed_password = hash_password(user_in.password)
        user = User(
            email=user_in.email,
            full_name=user_in.full_name,
            password=hashed_password,
        )

        session.add(user)
        session.commit()
        session.refresh(user)

    return UserOut.model_validate(user)
