import os
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

DATABASE_PATH = Path(
    os.getenv(
        "DATABASE_PATH",
        str(BASE_DIR / "logs.db")
    )
)


def get_connection():
    """
    Create and return a SQLite database connection.

    DATABASE_PATH can be configured through the
    DATABASE_PATH environment variable.

    Default:
        project_root/logs.db

    Docker:
        /app/data/logs.db
    """

    try:
        DATABASE_PATH.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        connection = sqlite3.connect(
            DATABASE_PATH,
            timeout=10
        )

        connection.row_factory = sqlite3.Row

        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        return connection

    except sqlite3.Error as error:
        raise sqlite3.Error(
            f"Unable to connect to database: {error}"
        ) from error
