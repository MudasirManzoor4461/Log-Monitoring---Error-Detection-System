from app.database.connection import get_connection


def create_tables():
    """
    Create all required database tables safely.
    """

    connection = None

    try:
        connection = get_connection()

        cursor = connection.cursor()

        # -----------------------------
        # Logs table
        # -----------------------------
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

        # -----------------------------
        # Alerts table
        # -----------------------------
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

        # -----------------------------
        # Prevent duplicate alerts
        # -----------------------------
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_alerts_unique_log_id
            ON alerts(log_id)
            WHERE log_id IS NOT NULL
        """)

        connection.commit()

        print("Database tables created successfully.")

    except Exception as error:

        if connection:
            connection.rollback()

        print(
            f"Error creating database tables: {error}"
        )

        raise

    finally:

        if connection:
            connection.close()