from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, Field, validator


class BaseWithORM(BaseModel):
    name: str

    class Config:
        orm_model = True


class UserCreate(BaseWithORM):
    password: str


class UserInDB(BaseWithORM):
    hashed_password: str


class UserBase(BaseWithORM):
    id: int


class UserRedis(UserBase):
    is_active: bool


class UserToken(BaseModel):
    token: UUID4 = Field(..., alias="access_token")
    expires: datetime
    token_type: Optional[str] = 'bearer'

    class Config:
        orm_model = True
        allow_population_by_field_name = True

        @validator("token")
        def hexlify_token(cls, value):
            """Конвертирует UUID в hex строку"""
            return value.hex
