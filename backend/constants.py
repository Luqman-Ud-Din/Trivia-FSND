import os
from enum import Enum

QUESTIONS_PER_PAGE = 10


class StatusCode(Enum):
    """Enum to maintain status codes."""

    HTTP_200_OK = 200
    HTTP_201_CREATED = 201
    HTTP_204_NO_CONTENT = 204
    HTTP_400_BAD_REQUEST = 400
    HTTP_401_UNAUTHORIZED = 401
    HTTP_403_FORBIDDEN = 403
    HTTP_404_NOT_FOUND = 404
    HTTP_405_METHOD_NOT_ALLOWED = 405
    HTTP_422_UNPROCESSABLE_ENTITY = 422
    HTTP_500_INTERNAL_SERVER_ERROR = 500


DATABASE_CONFIGURATION = {
    'username': os.environ.get('DATABASE_USER') or '',
    'password': os.environ.get('DATABASE_PASSWORD') or '',
    'name': os.environ.get('DATABASE_NAME') or 'trivia',
    'host': os.environ.get('DATABASE_HOST') or 'localhost',
    'port': os.environ.get('DATABASE_PORT') or '5432',
}

DATABASE_PATH = "postgres://{username}:{password}@{host}:{port}/{name}".format(
    **DATABASE_CONFIGURATION
)
