from pydantic import BaseModel, ConfigDict, EmailStr


class UserIn(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: str
    full_name: str
