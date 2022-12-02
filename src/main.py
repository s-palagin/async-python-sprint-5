import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_pagination import add_pagination

from api.v1 import files, users
from core.config import app_settings
from core.logger import logger

app = FastAPI(
    title=app_settings.app_title,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    redoc_url=None
)

app.include_router(files.router, prefix='/api/v1', tags=['files'])
app.include_router(users.router, prefix='/api/v1', tags=['users'])


add_pagination(app)


if __name__ == "__main__":
    logger.info('Start server.')
    uvicorn.run(
        'main:app',
        host=app_settings.project_host,
        port=app_settings.project_port,
    )
