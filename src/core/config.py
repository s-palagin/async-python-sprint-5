import os

import redis
from pydantic import BaseSettings


class AppSettings(BaseSettings):
    app_title: str = "FastApi File Server"
    db_user: str = 'postgres'
    db_password: str = 'postgres'
    db_name: str = 'postgres'
    db_port: int = 5432

    project_host: str = '127.0.0.1'
    project_port: int = 8000
    database_dsn: str = (
        f'postgresql+asyncpg://{db_user}:{db_password}'
        f'@{project_host}:{db_port}/{db_name}'
    )
    algorithm: str = "sha256"
    hmac_iteration = 10_000
    access_token_expire_minutes = 300
    file_folder = 'user_file'
    test_db_name = 'test_db'
    test_database: str = (
        'postgresql+asyncpg://postgres:postgres@localhost:5432/test_db'
    )
    secret_key: str = (
        '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
    )

    class Config:
        env_file = '.env'


app_settings = AppSettings()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
re_cli = redis.Redis()
