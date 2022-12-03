import time

from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi_pagination import Page, paginate
from fastapi_pagination.ext.sqlalchemy import AbstractPage
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import re_cli
from db.db import get_session
from models.users import UsersTable as User
from schemas.files import FileInDB, UploadResponse
from services.files import files_crud
from services.users import get_current_user

router = APIRouter()


@router.get('/ping', description='Checks the availability of services.')
async def get_ping(
        db: AsyncSession = Depends(get_session),
        user: User = Depends(get_current_user),
) -> dict:
    start_time = time.time()
    await files_crud.get(db=db, user=user)
    ping_db = time.time() - start_time
    start_time = time.time()
    re_cli.get('nothing')
    ping_redis = time.time() - start_time
    return {
        'datebase': "{:.4f}".format(ping_db),
        'redis': "{:.4f}".format(ping_redis),
        'user': {'name': user.name, 'id': user.id},
    }


@router.get(
    '/list',
    response_model=Page[FileInDB],
    description='Get user file list.'
)
async def get_files_list(
        db: AsyncSession = Depends(get_session),
        user: User = Depends(get_current_user),
) -> AbstractPage:
    files = await files_crud.get(db=db, user=user)
    return paginate(files)


@router.post(
    '/upload',
    status_code=status.HTTP_201_CREATED,
    description='Upload user file.',
    response_model=UploadResponse,
    response_model_exclude_unset=True
)
async def upload_file(
    path: str,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    file: UploadFile = File(),
) -> UploadResponse:
    file_upload = await files_crud.create(
        db=db, file=file, user=user, path=path)
    return UploadResponse(**file_upload)


@router.get(
    '/download',
    description='Download user file.',
    response_class=FileResponse
)
async def download_file(
        *,
        db: AsyncSession = Depends(get_session),
        user: User = Depends(get_current_user),
        identifier: str | int = None,
        download_folder: bool = False,
) -> FileResponse:
    if download_folder:
        file = await files_crud.download_folder(user=user, path=identifier)
    else:
        file = await files_crud.download_file(
            db=db, user=user, identifier=identifier)
    return file
