# from typing import Any
import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import re_cli
from db.db import get_session
from schemas import users as schema
from services.users import get_current_user, token_crud, user_crud
from services.utils import user_str, validate_password

router = APIRouter()


@router.post(
    '/register',
    description='New user registration.',
    status_code=status.HTTP_201_CREATED,
    response_model=schema.UserBase
)
async def register_user(
    user: schema.UserCreate,
    db: AsyncSession = Depends(get_session)
) -> schema.UserBase:
    answer = await user_crud.add(db=db, obj_in=user)
    return schema.UserBase(id=answer.id, name=answer.name)


@router.post(
    '/auth',
    description='Get token.',
    status_code=status.HTTP_201_CREATED,
    response_model=schema.UserToken
)
async def auth(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session)
) -> schema.UserToken:
    user = await user_crud.get_user_from_name(db=db, name=form_data.username)
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect name or password")
    if not validate_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=400, detail="Incorrect name or password")
    token = await token_crud.create_token(db=db, id=user.id)
    re_cli.set(
        str(token.token),
        json.dumps(
            {'expires': token.expires.timestamp(), 'user': user_str(user)}
        )
    )
    return schema.UserToken(access_token=token.token, expires=token.expires)


@router.get(
    '/me',
    response_model=schema.UserBase,
    description='Get current user')
async def read_users_me(
    current_user=Depends(get_current_user)
) -> schema.UserBase:
    return schema.UserBase(id=current_user.id, name=current_user.name)
