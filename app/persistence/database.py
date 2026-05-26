import os

DEFAULT_DATABASE_URL = "postgresql://modernization:modernization@localhost:5432/modernization"


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

