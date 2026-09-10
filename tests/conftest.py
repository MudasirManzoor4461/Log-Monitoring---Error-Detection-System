import sqlite3

import pytest


@pytest.fixture
def test_database(tmp_path, monkeypatch):
    db_path = tmp_path / "test_logs.db"

    def get_test_connection():
        connection = sqlite3.connect(db_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    connection = get_test_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                category TEXT,
                UNIQUE(timestamp, level, message)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_id INTEGER,
                level TEXT NOT NULL,
                category TEXT,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL,
                acknowledged INTEGER NOT NULL DEFAULT 0
                    CHECK (acknowledged IN (0, 1)),
                FOREIGN KEY (log_id)
                    REFERENCES logs(id)
                    ON DELETE SET NULL
            )
        """)

        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_alerts_unique_log_id
            ON alerts(log_id)
            WHERE log_id IS NOT NULL
        """)

        connection.commit()

    finally:
        connection.close()

    monkeypatch.setattr(
        "app.database.repositories.get_connection",
        get_test_connection
    )

    return db_path