from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)
    full_name: str = Field(min_length=5, max_length=64)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: str
    full_name: str
    id: int
