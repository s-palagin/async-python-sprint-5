import json
import os
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from typing import Generic, Optional, Type, TypeVar, Union
from zipfile import ZipFile

import aiofiles
from fastapi import File, HTTPException, status, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from sqlalchemy import and_, exc, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import app_settings, re_cli
from core.logger import logger
from db.db import Base
from models.users import TokensTable, UsersTable

from .utils import hash_password, user_obj

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)


class RepositoryDBUser(Generic[ModelType, CreateSchemaType]):
    def __init__(self, user_model: Type[ModelType]) -> None:
        self._user_model = user_model

    async def add(
        self,
        db: AsyncSession,
        obj_in: CreateSchemaType
    ) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        hashed_password = hash_password(obj_in_data.pop('password'))
        obj_in_data['hashed_password'] = hashed_password
        db_obj = self._user_model(**obj_in_data)
        db.add(db_obj)
        try:
            await db.commit()
            await db.refresh(db_obj)
        except exc.IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Select another name'
            )
        except exc.SQLAlchemyError as error:
            logger.error(error)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        return db_obj

    async def get_user_from_name(
        self,
        db: AsyncSession,
        name: str
    ) -> Optional[ModelType]:
        statement = select(self._user_model).where(
            self._user_model.name == name)
        user = await db.execute(statement=statement)
        return user.scalar_one_or_none()

    async def get_user_by_token(
        self,
        db: AsyncSession,
        token: str
    ) -> Optional[ModelType]:
        from_redis = json.loads(re_cli.get(token))
        if from_redis:
            if datetime.utcfromtimestamp(
                from_redis.get('expires')
            ) > datetime.now():
                return user_obj(from_redis.get('user'))
            re_cli.delete(token)
        query = select(self._user_model).join(TokensTable).where(
            and_(
                TokensTable.token == token,
                TokensTable.expires > datetime.now()
            )
        )
        user = await db.execute(query)
        return user.scalar_one_or_none()


class RepositoryDBToken(Generic[ModelType, CreateSchemaType]):
    def __init__(self, token_model: Type[ModelType]) -> None:
        self._token_model = token_model

    async def create_token(
        self,
        db: AsyncSession,
        id: int
    ) -> ModelType:
        db_obj = self._token_model(
            user_id=id,
            expires=datetime.now() + timedelta(
                minutes=app_settings.access_token_expire_minutes))
        db.add(db_obj)
        try:
            await db.commit()
            await db.refresh(db_obj)
        except exc.SQLAlchemyError as error:
            logger.error(error)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        return db_obj


class RepositoryDBFile(Generic[ModelType, CreateSchemaType]):
    def __init__(self, model: Type[ModelType]) -> None:
        self._model = model

    async def get(
            self,
            db: AsyncSession,
            user: UsersTable
    ) -> list:
        statement = (
            select(self._model)
            .where(
                self._model.author == user.id
            )
        )
        result = await db.scalars(statement=statement)
        logger.debug(str(result))
        return result.all()

    async def get_path_by_id(
        self,
        db: AsyncSession,
        user: ModelType,
        id: int
    ) -> str:
        statement = select(self._model).where(self._model.id == id)
        file = await db.scalar(statement=statement)
        full_path = (
            f'{app_settings.file_folder}/{user.name}/{file.path}/{file.name}'
        )
        logger.info(file.name)
        return full_path

    async def get_file_by_id(
        self,
        db: AsyncSession,
        user: UsersTable,
        id: int
    ) -> File:
        path = await self.get_path_by_id(db=db, id=id, user=user)
        if os.path.exists(path) and os.path.isfile(path):
            return FileResponse(path=path)
        raise HTTPException(
            status_code=404, detail="Item not found"
        )

    @staticmethod
    async def get_file_by_path(user: UsersTable, path: Path) -> File:
        logger.info(path)
        full_path = f'{app_settings.file_folder}/{user.name}/{path}'
        if os.path.exists(path) and os.path.isfile(path):
            return FileResponse(path=full_path)
        raise HTTPException(
            status_code=404, detail="Item not found"
        )

    async def download_file(
            self,
            db: AsyncSession,
            user: UsersTable,
            identifier: Union[str, int],
    ) -> File:
        try:
            int(identifier)
            logger.info(f'{identifier} is int')
            file = await self.get_file_by_id(
                db=db,
                user=user,
                id=int(identifier),
            )
        except ValueError:
            logger.info(identifier)
            file = await self.get_file_by_path(
                user=user,
                path=Path(identifier),
            )
        return file

    @staticmethod
    def zip_folder(file_list: list) -> File:
        io = BytesIO()
        zip_name = f'{str(datetime.now())}.zip'
        with ZipFile(io, 'w') as zip:
            for file in file_list:
                zip.write(file)
        return StreamingResponse(
            iter([io.getvalue()]),
            media_type='application/x-zip-compressed',
            headers={'Content-Disposition': f'attachment filename={zip_name}'}
        )

    async def download_folder(
            self,
            user: UsersTable,
            path: str,
    ) -> File:
        full_path = f'{app_settings.file_folder}/{user.name}/{path}'
        file_list = [
            f'{full_path}/{file.name}' for file in list(
                Path(full_path).iterdir()
            )
        ]
        archive = self.zip_folder(file_list)
        return archive

    async def create_in_db(
            self,
            size: int,
            db: AsyncSession,
            user: UsersTable,
            path: str,
            file: UploadFile = File(),
    ) -> ModelType:
        db_obj = self._model(
            name=file.filename,
            path=path,
            size=size,
            is_downloadable=True,
            author=user.id
        )
        db.add(db_obj)
        try:
            await db.commit()
            await db.refresh(db_obj)
        except exc.SQLAlchemyError as error:
            logger.error(error)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        return db_obj

    @staticmethod
    async def write_file(
            user: UsersTable,
            path: str,
            file: UploadFile = File(),
    ) -> None:
        file.file.seek(0)
        content = file.file.read()
        user_path = app_settings.file_folder + f'/{user.name}'
        p = Path(f'{user_path}/{path}' if path else user_path)
        try:
            if not Path.exists(p):
                Path(p).mkdir(parents=True, exist_ok=True)
                logger.info(f'mkdir {user_path}')
            async with aiofiles.open(Path(p, file.filename), 'wb') as f:
                logger.debug(f)
                await f.write(content)
        except Exception as ex:
            logger.error(ex)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='File not saved'
            )

    async def create(
            self,
            db: AsyncSession,
            user: UsersTable,
            path: str,
            file: UploadFile = File(),
    ) -> dict:
        file_size = len(await file.read())
        result = await self.write_file(
            user=user,
            path=path,
            file=file,
        )
        logger.info(str(result))
        if not isinstance(result, Exception):
            await self.create_in_db(
                db=db,
                user=user,
                path=path,
                file=file,
                size=file_size,
            )
            return {
                'Ready': f'Successfully uploaded {file.filename}',
                'Size': f'{"{:.3f}".format(file_size/1024)}kb',
            }
        return {'Error': str(result)}
