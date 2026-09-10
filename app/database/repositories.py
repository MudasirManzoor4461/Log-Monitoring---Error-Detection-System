import sqlite3
from datetime import datetime

from app.database.connection import get_connection


TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

VALID_LEVELS = {
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL"
}


def save_logs(logs):
    """
    Save valid logs into the database.

    Returns a result dictionary containing:
    - success
    - inserted_logs
    - duplicate_logs
    - skipped_logs

    Duplicate logs are ignored because the database
    has a UNIQUE constraint on timestamp, level and message.
    """

    if logs is None or not isinstance(logs, list):

        return {
            "success": False,
            "inserted_logs": 0,
            "duplicate_logs": 0,
            "skipped_logs": 0
        }

    connection = None

    inserted_logs = 0
    duplicate_logs = 0
    skipped_logs = 0

    try:

        connection = get_connection()
        cursor = connection.cursor()

        for log in logs:

            # -----------------------------
            # Validate log object
            # -----------------------------

            if not isinstance(log, dict):

                skipped_logs += 1
                continue

            timestamp = log.get("timestamp")
            level = log.get("level")
            message = log.get("message")
            category = log.get("category")

            # -----------------------------
            # Validate required fields
            # -----------------------------

            if not all(
                isinstance(value, str)
                for value in (
                    timestamp,
                    level,
                    message
                )
            ):

                skipped_logs += 1
                continue

            timestamp = timestamp.strip()
            level = level.strip().upper()
            message = message.strip()

            # -----------------------------
            # Validate timestamp
            # -----------------------------

            try:

                datetime.strptime(
                    timestamp,
                    TIMESTAMP_FORMAT
                )

            except ValueError:

                skipped_logs += 1
                continue

            # -----------------------------
            # Validate level
            # -----------------------------

            if level not in VALID_LEVELS:

                skipped_logs += 1
                continue

            # -----------------------------
            # Validate message
            # -----------------------------

            if not message:

                skipped_logs += 1
                continue

            # -----------------------------
            # Normalize category
            # -----------------------------

            if isinstance(category, str):

                category = category.strip()

                if not category:
                    category = None

            else:

                category = None

            # -----------------------------
            # Insert log
            # -----------------------------

            cursor.execute(
                """
                INSERT OR IGNORE INTO logs
                (timestamp, level, message, category)
                VALUES (?, ?, ?, ?)
                """,
                (
                    timestamp,
                    level,
                    message,
                    category
                )
            )

            # -----------------------------
            # Check whether insertion happened
            # -----------------------------

            if cursor.rowcount == 1:

                inserted_logs += 1

            else:

                duplicate_logs += 1

        # -----------------------------
        # Commit transaction
        # -----------------------------

        connection.commit()

        return {
            "success": True,
            "inserted_logs": inserted_logs,
            "duplicate_logs": duplicate_logs,
            "skipped_logs": skipped_logs
        }

    except sqlite3.Error as error:

        # Roll back partial changes if a database
        # error occurs before commit.
        if connection is not None:

            try:
                connection.rollback()

            except sqlite3.Error:
                pass

        print(
            f"Database error while saving logs: {error}"
        )

        return {
            "success": False,
            "inserted_logs": 0,
            "duplicate_logs": 0,
            "skipped_logs": skipped_logs
        }

    finally:

        if connection is not None:
            connection.close()


def get_all_logs():
    """
    Return all logs from the database.
    """

    connection = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM logs
            ORDER BY timestamp ASC, id ASC
            """
        )

        return cursor.fetchall()

    except sqlite3.Error as error:

        print(
            f"Database error while fetching logs: {error}"
        )

        return []

    finally:

        if connection is not None:
            connection.close()


def get_logs_by_level(level):
    """
    Return logs matching a specific log level.
    """

    if not isinstance(level, str):
        return []

    level = level.strip().upper()

    if level not in VALID_LEVELS:
        return []

    connection = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM logs
            WHERE level = ?
            ORDER BY timestamp ASC, id ASC
            """,
            (level,)
        )

        return cursor.fetchall()

    except sqlite3.Error as error:

        print(
            f"Database error while filtering by level: {error}"
        )

        return []

    finally:

        if connection is not None:
            connection.close()


def get_logs_by_category(category):
    """
    Return logs matching a specific error category.
    """

    if not isinstance(category, str):
        return []

    category = category.strip()

    if not category:
        return []

    connection = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM logs
            WHERE category = ?
            ORDER BY timestamp ASC, id ASC
            """,
            (category,)
        )

        return cursor.fetchall()

    except sqlite3.Error as error:

        print(
            f"Database error while filtering by category: {error}"
        )

        return []

    finally:

        if connection is not None:
            connection.close()


def get_logs_by_time_range(start_time, end_time):
    """
    Return logs between start_time and end_time.

    Both timestamps must use:
    YYYY-MM-DD HH:MM:SS
    """

    if not isinstance(start_time, str):
        return []

    if not isinstance(end_time, str):
        return []

    start_time = start_time.strip()
    end_time = end_time.strip()

    # -----------------------------
    # Validate timestamps
    # -----------------------------

    try:

        start_datetime = datetime.strptime(
            start_time,
            TIMESTAMP_FORMAT
        )

        end_datetime = datetime.strptime(
            end_time,
            TIMESTAMP_FORMAT
        )

    except ValueError:

        return []

    # -----------------------------
    # Validate time range
    # -----------------------------

    if start_datetime > end_datetime:
        return []

    connection = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM logs
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC, id ASC
            """,
            (
                start_time,
                end_time
            )
        )

        return cursor.fetchall()

    except sqlite3.Error as error:

        print(
            f"Database error while filtering by time: {error}"
        )

        return []

    finally:

        if connection is not None:
            connection.close()


def delete_log_by_id(log_id):
    """
    Delete a single log by its database ID safely.

    Returns:
        dict containing:
        - success
        - deleted
        - message
    """

    # Validate ID type
    if isinstance(log_id, bool) or not isinstance(log_id, int):
        return {
            "success": False,
            "deleted": False,
            "message": "Invalid log ID. ID must be an integer."
        }

    # ID must be positive
    if log_id <= 0:
        return {
            "success": False,
            "deleted": False,
            "message": "Invalid log ID. ID must be greater than 0."
        }

    connection = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM logs
            WHERE id = ?
            """,
            (log_id,)
        )

        # Check whether a record was actually deleted
        if cursor.rowcount == 0:
            connection.rollback()

            return {
                "success": False,
                "deleted": False,
                "message": "Log not found."
            }

        connection.commit()

        return {
            "success": True,
            "deleted": True,
            "message": "Log deleted successfully."
        }

    except sqlite3.Error as error:

        if connection is not None:
            try:
                connection.rollback()
            except sqlite3.Error:
                pass

        print(
            f"Database error while deleting log: {error}"
        )

        return {
            "success": False,
            "deleted": False,
            "message": "Database error while deleting log."
        }

    finally:

        if connection is not None:
            connection.close()

            
def search_logs_by_message(
    search_term,
    page=1,
    page_size=10
):
    """
    Search logs by message content with pagination.

    Search is case-insensitive.
    """

    if not isinstance(search_term, str):
        return {
            "success": False,
            "logs": [],
            "total_logs": 0,
            "page": page,
            "page_size": page_size,
            "total_pages": 0,
            "has_next": False,
            "has_previous": False,
            "message": "Invalid search query."
        }

    search_term = search_term.strip()

    if not search_term:
        return {
            "success": False,
            "logs": [],
            "total_logs": 0,
            "page": page,
            "page_size": page_size,
            "total_pages": 0,
            "has_next": False,
            "has_previous": False,
            "message": "Search query cannot be empty."
        }

    if isinstance(page, bool) or not isinstance(page, int):
        return {
            "success": False,
            "logs": [],
            "total_logs": 0,
            "page": page,
            "page_size": page_size,
            "total_pages": 0,
            "has_next": False,
            "has_previous": False,
            "message": "Invalid page. Page must be an integer."
        }

    if page < 1:
        return {
            "success": False,
            "logs": [],
            "total_logs": 0,
            "page": page,
            "page_size": page_size,
            "total_pages": 0,
            "has_next": False,
            "has_previous": False,
            "message": "Invalid page. Page must be greater than 0."
        }

    if isinstance(page_size, bool) or not isinstance(page_size, int):
        return {
            "success": False,
            "logs": [],
            "total_logs": 0,
            "page": page,
            "page_size": page_size,
            "total_pages": 0,
            "has_next": False,
            "has_previous": False,
            "message": "Invalid page size. Page size must be an integer."
        }

    if page_size < 1:
        return {
            "success": False,
            "logs": [],
            "total_logs": 0,
            "page": page,
            "page_size": page_size,
            "total_pages": 0,
            "has_next": False,
            "has_previous": False,
            "message": "Invalid page size. Page size must be greater than 0."
        }

    connection = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        search_pattern = f"%{search_term}%"

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM logs
            WHERE message LIKE ? COLLATE NOCASE
            """,
            (search_pattern,)
        )

        total_logs = cursor.fetchone()[0]

        total_pages = (
            (total_logs + page_size - 1) // page_size
            if total_logs > 0
            else 0
        )

        offset = (page - 1) * page_size

        cursor.execute(
            """
            SELECT *
            FROM logs
            WHERE message LIKE ? COLLATE NOCASE
            ORDER BY timestamp ASC, id ASC
            LIMIT ? OFFSET ?
            """,
            (
                search_pattern,
                page_size,
                offset
            )
        )

        logs = cursor.fetchall()

        return {
            "success": True,
            "logs": logs,
            "total_logs": total_logs,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": (
                page > 1 and total_pages > 0
            )
        }

    except sqlite3.Error as error:

        print(
            f"Database error while searching logs: {error}"
        )

        return {
            "success": False,
            "logs": [],
            "total_logs": 0,
            "page": page,
            "page_size": page_size,
            "total_pages": 0,
            "has_next": False,
            "has_previous": False,
            "message": "Database error while searching logs."
        }

    finally:

        if connection is not None:
            connection.close()


def save_alert(alert):
    """
    Save a single alert safely into the database.

    Duplicate alerts for the same log_id are prevented.
    """

    if not isinstance(alert, dict):
        return {
            "success": False,
            "message": "Invalid alert data."
        }

    level = alert.get("level")
    category = alert.get("category")
    message = alert.get("message")
    log_id = alert.get("log_id")
    created_at = alert.get("created_at")

    if not isinstance(level, str) or not level.strip():
        return {
            "success": False,
            "message": "Alert level is required."
        }

    if not isinstance(message, str) or not message.strip():
        return {
            "success": False,
            "message": "Alert message is required."
        }

    if category is not None and not isinstance(category, str):
        return {
            "success": False,
            "message": "Alert category must be a string."
        }

    if log_id is not None:

        if isinstance(log_id, bool) or not isinstance(log_id, int):
            return {
                "success": False,
                "message": "Invalid log ID."
            }

        if log_id <= 0:
            return {
                "success": False,
                "message": "Log ID must be greater than 0."
            }

    if not isinstance(created_at, str) or not created_at.strip():
        created_at = datetime.now().strftime(
            TIMESTAMP_FORMAT
        )

    connection = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        # -----------------------------
        # Check for duplicate alert
        # -----------------------------

        if log_id is not None:

            cursor.execute(
                """
                SELECT id
                FROM alerts
                WHERE log_id = ?
                LIMIT 1
                """,
                (log_id,)
            )

            existing_alert = cursor.fetchone()

            if existing_alert is not None:

                connection.commit()

                return {
                    "success": True,
                    "alert_id": existing_alert["id"],
                    "inserted": False,
                    "message": "Alert already exists for this log."
                }

        # -----------------------------
        # Insert new alert
        # -----------------------------

        cursor.execute(
            """
            INSERT INTO alerts (
                log_id,
                level,
                category,
                message,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                log_id,
                level.strip().upper(),
                category.strip()
                if isinstance(category, str)
                else None,
                message.strip(),
                created_at.strip()
            )
        )

        connection.commit()

        return {
            "success": True,
            "alert_id": cursor.lastrowid,
            "inserted": True,
            "message": "Alert saved successfully."
        }

    except sqlite3.IntegrityError:

        if connection is not None:

            try:
                connection.rollback()
            except sqlite3.Error:
                pass

        # Another process may have created the same alert
        # between the duplicate check and INSERT.
        if log_id is not None:

            try:
                cursor = connection.cursor()

                cursor.execute(
                    """
                    SELECT id
                    FROM alerts
                    WHERE log_id = ?
                    LIMIT 1
                    """,
                    (log_id,)
                )

                existing_alert = cursor.fetchone()

                if existing_alert is not None:

                    return {
                        "success": True,
                        "alert_id": existing_alert["id"],
                        "inserted": False,
                        "message": "Alert already exists for this log."
                    }

            except sqlite3.Error:
                pass

        return {
            "success": False,
            "message": "Unable to save alert because of a database constraint."
        }

    except sqlite3.Error as error:

        if connection is not None:

            try:
                connection.rollback()
            except sqlite3.Error:
                pass

        print(
            f"Database error while saving alert: {error}"
        )

        return {
            "success": False,
            "message": "Database error while saving alert."
        }

    finally:

        if connection is not None:
            connection.close()


def get_all_alerts():
    """
    Return all alerts from the database.
    """

    connection = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                log_id,
                level,
                category,
                message,
                created_at,
                acknowledged
            FROM alerts
            ORDER BY id DESC
            """
        )

        return cursor.fetchall()

    except sqlite3.Error as error:

        print(
            f"Database error while fetching alerts: {error}"
        )

        return []

    finally:

        if connection is not None:
            connection.close()


def get_unacknowledged_alerts():
    """
    Return all alerts that have not been acknowledged.
    """

    connection = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                log_id,
                level,
                category,
                message,
                created_at,
                acknowledged
            FROM alerts
            WHERE acknowledged = 0
            ORDER BY id DESC
            """
        )

        return cursor.fetchall()

    except sqlite3.Error as error:

        print(
            "Database error while fetching "
            f"unacknowledged alerts: {error}"
        )

        return []

    finally:

        if connection is not None:
            connection.close()


def acknowledge_alert(alert_id):
    """
    Mark an alert as acknowledged.
    """

    if isinstance(alert_id, bool) or not isinstance(alert_id, int):
        return {
            "success": False,
            "updated": False,
            "message": "Invalid alert ID."
        }

    if alert_id <= 0:
        return {
            "success": False,
            "updated": False,
            "message": "Alert ID must be greater than 0."
        }

    connection = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE alerts
            SET acknowledged = 1
            WHERE id = ?
            """,
            (alert_id,)
        )

        if cursor.rowcount == 0:

            connection.rollback()

            return {
                "success": False,
                "updated": False,
                "message": "Alert not found."
            }

        connection.commit()

        return {
            "success": True,
            "updated": True,
            "message": "Alert acknowledged successfully."
        }

    except sqlite3.Error as error:

        if connection is not None:

            try:
                connection.rollback()
            except sqlite3.Error:
                pass

        print(
            f"Database error while acknowledging alert: {error}"
        )

        return {
            "success": False,
            "updated": False,
            "message": "Database error while acknowledging alert."
        }

    finally:

        if connection is not None:
            connection.close()

def save_log_and_get_id(log):
    """
    Save a single valid log and return its database ID.

    If the log already exists, return the existing log ID.

    This function is useful when another database record,
    such as an alert, needs to reference the saved log.
    """

    if not isinstance(log, dict):
        return {
            "success": False,
            "log_id": None,
            "inserted": False,
            "message": "Invalid log data."
        }

    timestamp = log.get("timestamp")
    level = log.get("level")
    message = log.get("message")
    category = log.get("category")

    if not all(
        isinstance(value, str)
        for value in (
            timestamp,
            level,
            message
        )
    ):
        return {
            "success": False,
            "log_id": None,
            "inserted": False,
            "message": "Invalid log fields."
        }

    timestamp = timestamp.strip()
    level = level.strip().upper()
    message = message.strip()

    try:
        datetime.strptime(
            timestamp,
            TIMESTAMP_FORMAT
        )
    except ValueError:
        return {
            "success": False,
            "log_id": None,
            "inserted": False,
            "message": "Invalid timestamp."
        }

    if level not in VALID_LEVELS:
        return {
            "success": False,
            "log_id": None,
            "inserted": False,
            "message": "Invalid log level."
        }

    if not message:
        return {
            "success": False,
            "log_id": None,
            "inserted": False,
            "message": "Log message cannot be empty."
        }

    if isinstance(category, str):
        category = category.strip()

        if not category:
            category = None
    else:
        category = None

    connection = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT OR IGNORE INTO logs
            (timestamp, level, message, category)
            VALUES (?, ?, ?, ?)
            """,
            (
                timestamp,
                level,
                message,
                category
            )
        )

        if cursor.rowcount == 1:

            log_id = cursor.lastrowid

            connection.commit()

            return {
                "success": True,
                "log_id": log_id,
                "inserted": True,
                "message": "Log saved successfully."
            }

        # Log already exists.
        cursor.execute(
            """
            SELECT id
            FROM logs
            WHERE timestamp = ?
              AND level = ?
              AND message = ?
            LIMIT 1
            """,
            (
                timestamp,
                level,
                message
            )
        )

        existing_log = cursor.fetchone()

        if existing_log is None:

            connection.rollback()

            return {
                "success": False,
                "log_id": None,
                "inserted": False,
                "message": "Unable to find saved log."
            }

        connection.commit()

        return {
            "success": True,
            "log_id": existing_log["id"],
            "inserted": False,
            "message": "Log already exists."
        }

    except sqlite3.Error as error:

        if connection is not None:

            try:
                connection.rollback()
            except sqlite3.Error:
                pass

        print(
            f"Database error while saving log: {error}"
        )

        return {
            "success": False,
            "log_id": None,
            "inserted": False,
            "message": "Database error while saving log."
        }

    finally:

        if connection is not None:
            connection.close()
            