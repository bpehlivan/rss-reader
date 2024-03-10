from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int
    redis_url: str = "redis://localhost:6379/0"
    postgres_test_db: str = "test"

    secret: str = "secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    class Config:
        # last file will overwrite the previous ones
        env_file = [".env.example", ".env"]
        extra = "allow"


settings = Settings()
