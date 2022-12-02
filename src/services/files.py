from models.files import FileModel
from schemas.files import FileCreate

from .base import RepositoryDBFile


class RepositoryFile(RepositoryDBFile[FileModel, FileCreate]):
    pass


files_crud = RepositoryFile(FileModel)
