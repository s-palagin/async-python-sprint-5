from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class FileBase(BaseModel):
    name: str


class FileCreate(FileBase):
    pass


class FileUpload(BaseModel):
    path: str


class FileInDBBase(FileBase):
    id: int
    created_at: datetime
    path: Optional[str]
    size: int
    is_downloadable: bool

    class Config:
        orm_mode = True


class File(FileInDBBase):
    pass


class FileInDB(FileInDBBase):
    pass
