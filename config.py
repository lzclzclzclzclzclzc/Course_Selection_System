import os
from datetime import timedelta
from urllib.parse import quote_plus


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)


class SQLiteConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URI",
        "sqlite:///./student_course.db",
    )


def get_opengauss_uri():
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "postgres")
    DB_USER = os.getenv("DB_USER", "gaussdb")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "Enmo123")
    encoded_password = quote_plus(DB_PASSWORD)
    return f"postgresql+psycopg2://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}?client_encoding=utf8"


class OpenGaussConfig(Config):
    SQLALCHEMY_DATABASE_URI = get_opengauss_uri()
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {
            "options": "-c timezone=UTC"
        }
    }
