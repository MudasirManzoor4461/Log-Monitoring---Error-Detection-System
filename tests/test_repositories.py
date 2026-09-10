import sqlite3
from unittest.mock import patch


from app.database.repositories import (
    save_logs,
    get_all_logs,
    get_logs_by_level,
    get_logs_by_category,
    get_logs_by_time_range,
    delete_log_by_id,
    search_logs_by_message,
    save_alert,
    get_all_alerts,
    get_unacknowledged_alerts,
    acknowledge_alert,
    save_log_and_get_id,
)


# ============================================================
# save_logs()
# ============================================================

def test_save_logs(test_database):
    logs = [
        {
            "timestamp": "2026-09-10 10:00:00",
            "level": "INFO",
            "message": "Server started",
            "category": None,
        },
        {
            "timestamp": "2026-09-10 10:01:00",
            "level": "ERROR",
            "message": "Database connection failed",
            "category": "DATABASE_ERROR",
        },
    ]

    result = save_logs(logs)

    assert result["success"] is True
    assert result["inserted_logs"] == 2
    assert result["duplicate_logs"] == 0
    assert result["skipped_logs"] == 0


def test_save_duplicate_logs(test_database):
    log = {
        "timestamp": "2026-09-10 11:00:00",
        "level": "ERROR",
        "message": "Database connection failed",
        "category": "DATABASE_ERROR",
    }

    first_result = save_logs([log])
    second_result = save_logs([log])

    assert first_result["success"] is True
    assert first_result["inserted_logs"] == 1

    assert second_result["success"] is True
    assert second_result["inserted_logs"] == 0
    assert second_result["duplicate_logs"] == 1
    assert second_result["skipped_logs"] == 0


def test_save_logs_invalid_input(test_database):
    result = save_logs(None)

    assert result["success"] is False
    assert result["inserted_logs"] == 0
    assert result["duplicate_logs"] == 0
    assert result["skipped_logs"] == 0


def test_save_logs_skips_invalid_records(test_database):
    logs = [
        {
            "timestamp": "2026-09-10 12:00:00",
            "level": "INFO",
            "message": "Valid log",
            "category": None,
        },
        "invalid log",
        {
            "timestamp": "invalid timestamp",
            "level": "ERROR",
            "message": "Bad timestamp",
            "category": None,
        },
        {
            "timestamp": "2026-09-10 12:02:00",
            "level": "INVALID",
            "message": "Bad level",
            "category": None,
        },
        {
            "timestamp": "2026-09-10 12:03:00",
            "level": "ERROR",
            "message": "",
            "category": None,
        },
    ]

    result = save_logs(logs)

    assert result["success"] is True
    assert result["inserted_logs"] == 1
    assert result["skipped_logs"] == 4


def test_save_logs_database_error(test_database):
    logs = [
        {
            "timestamp": "2026-09-10 12:00:00",
            "level": "ERROR",
            "message": "Database failure",
            "category": "DATABASE_ERROR",
        }
    ]

    with patch(
        "app.database.repositories.get_connection",
        side_effect=sqlite3.Error("Simulated database failure")
    ):
        result = save_logs(logs)

    assert result["success"] is False
    assert result["inserted_logs"] == 0
    assert result["duplicate_logs"] == 0


# ============================================================
# get_all_logs()
# ============================================================

def test_get_all_logs(test_database):
    logs = [
        {
            "timestamp": "2026-09-10 13:00:00",
            "level": "INFO",
            "message": "Server started",
            "category": None,
        },
        {
            "timestamp": "2026-09-10 13:01:00",
            "level": "ERROR",
            "message": "Database failed",
            "category": "DATABASE_ERROR",
        },
    ]

    save_logs(logs)

    result = get_all_logs()

    assert len(result) == 2
    assert result[0]["level"] == "INFO"
    assert result[1]["level"] == "ERROR"


# ============================================================
# get_logs_by_level()
# ============================================================

def test_get_logs_by_level(test_database):
    logs = [
        {
            "timestamp": "2026-09-10 14:00:00",
            "level": "INFO",
            "message": "Server started",
            "category": None,
        },
        {
            "timestamp": "2026-09-10 14:01:00",
            "level": "ERROR",
            "message": "Database failed",
            "category": "DATABASE_ERROR",
        },
        {
            "timestamp": "2026-09-10 14:02:00",
            "level": "ERROR",
            "message": "Another failure",
            "category": "API_ERROR",
        },
    ]

    save_logs(logs)

    result = get_logs_by_level("ERROR")

    assert len(result) == 2

    for log in result:
        assert log["level"] == "ERROR"


def test_get_logs_by_level_case_insensitive(test_database):
    save_logs([
        {
            "timestamp": "2026-09-10 15:00:00",
            "level": "ERROR",
            "message": "Database failed",
            "category": "DATABASE_ERROR",
        }
    ])

    result = get_logs_by_level("  error  ")

    assert len(result) == 1
    assert result[0]["level"] == "ERROR"


def test_get_logs_by_level_invalid_input(test_database):
    assert get_logs_by_level(None) == []
    assert get_logs_by_level("INVALID") == []
    assert get_logs_by_level("") == []


# ============================================================
# get_logs_by_category()
# ============================================================

def test_get_logs_by_category(test_database):
    logs = [
        {
            "timestamp": "2026-09-10 16:00:00",
            "level": "ERROR",
            "message": "Database failed",
            "category": "DATABASE_ERROR",
        },
        {
            "timestamp": "2026-09-10 16:01:00",
            "level": "CRITICAL",
            "message": "Payment gateway failed",
            "category": "PAYMENT_ERROR",
        },
        {
            "timestamp": "2026-09-10 16:02:00",
            "level": "ERROR",
            "message": "Another database failure",
            "category": "DATABASE_ERROR",
        },
    ]

    save_logs(logs)

    result = get_logs_by_category("DATABASE_ERROR")

    assert len(result) == 2

    for log in result:
        assert log["category"] == "DATABASE_ERROR"


def test_get_logs_by_category_invalid_input(test_database):
    assert get_logs_by_category(None) == []
    assert get_logs_by_category("") == []
    assert get_logs_by_category("   ") == []


# ============================================================
# get_logs_by_time_range()
# ============================================================

def test_get_logs_by_time_range(test_database):
    logs = [
        {
            "timestamp": "2026-09-10 17:00:00",
            "level": "INFO",
            "message": "First log",
            "category": None,
        },
        {
            "timestamp": "2026-09-10 17:30:00",
            "level": "ERROR",
            "message": "Second log",
            "category": "DATABASE_ERROR",
        },
        {
            "timestamp": "2026-09-10 18:00:00",
            "level": "CRITICAL",
            "message": "Third log",
            "category": "PAYMENT_ERROR",
        },
    ]

    save_logs(logs)

    result = get_logs_by_time_range(
        "2026-09-10 17:00:00",
        "2026-09-10 17:30:00",
    )

    assert len(result) == 2
    assert result[0]["message"] == "First log"
    assert result[1]["message"] == "Second log"


def test_get_logs_by_time_range_invalid_input(test_database):
    assert get_logs_by_time_range(
        None,
        "2026-09-10 18:00:00",
    ) == []

    assert get_logs_by_time_range(
        "invalid",
        "2026-09-10 18:00:00",
    ) == []

    assert get_logs_by_time_range(
        "2026-09-10 19:00:00",
        "2026-09-10 18:00:00",
    ) == []


# ============================================================
# delete_log_by_id()
# ============================================================

def test_delete_log_by_id(test_database):
    result = save_log_and_get_id({
        "timestamp": "2026-09-10 19:00:00",
        "level": "ERROR",
        "message": "Delete this log",
        "category": "DATABASE_ERROR",
    })

    log_id = result["log_id"]

    delete_result = delete_log_by_id(log_id)

    assert delete_result["success"] is True
    assert delete_result["deleted"] is True
    assert delete_result["message"] == "Log deleted successfully."

    logs = get_all_logs()

    assert len(logs) == 0


def test_delete_log_by_id_not_found(test_database):
    result = delete_log_by_id(99999)

    assert result["success"] is False
    assert result["deleted"] is False
    assert result["message"] == "Log not found."


def test_delete_log_by_id_invalid_input(test_database):
    result = delete_log_by_id(None)

    assert result["success"] is False
    assert result["deleted"] is False

    result = delete_log_by_id(0)

    assert result["success"] is False
    assert result["deleted"] is False

    result = delete_log_by_id(True)

    assert result["success"] is False
    assert result["deleted"] is False


# ============================================================
# search_logs_by_message()
# ============================================================

def test_search_logs_by_message(test_database):
    logs = [
        {
            "timestamp": "2026-09-10 20:00:00",
            "level": "ERROR",
            "message": "Database connection failed",
            "category": "DATABASE_ERROR",
        },
        {
            "timestamp": "2026-09-10 20:01:00",
            "level": "INFO",
            "message": "User logged in",
            "category": None,
        },
        {
            "timestamp": "2026-09-10 20:02:00",
            "level": "ERROR",
            "message": "Database timeout",
            "category": "DATABASE_ERROR",
        },
    ]

    save_logs(logs)

    result = search_logs_by_message("database")

    assert result["success"] is True
    assert result["total_logs"] == 2
    assert len(result["logs"]) == 2
    assert result["total_pages"] == 1
    assert result["has_next"] is False
    assert result["has_previous"] is False


def test_search_logs_case_insensitive(test_database):
    save_logs([
        {
            "timestamp": "2026-09-10 21:00:00",
            "level": "ERROR",
            "message": "Database Connection Failed",
            "category": "DATABASE_ERROR",
        }
    ])

    result = search_logs_by_message("DATABASE")

    assert result["success"] is True
    assert result["total_logs"] == 1


def test_search_logs_pagination(test_database):
    logs = []

    for number in range(1, 6):
        logs.append({
            "timestamp": f"2026-09-10 22:0{number}:00",
            "level": "ERROR",
            "message": f"Database error {number}",
            "category": "DATABASE_ERROR",
        })

    save_logs(logs)

    result = search_logs_by_message(
        "database",
        page=1,
        page_size=2,
    )

    assert result["success"] is True
    assert result["total_logs"] == 5
    assert len(result["logs"]) == 2
    assert result["total_pages"] == 3
    assert result["has_next"] is True
    assert result["has_previous"] is False


def test_search_logs_invalid_input(test_database):
    result = search_logs_by_message(None)

    assert result["success"] is False
    assert result["logs"] == []

    result = search_logs_by_message("database", page=0)

    assert result["success"] is False
    assert result["logs"] == []

    result = search_logs_by_message(
        "database",
        page_size=0,
    )

    assert result["success"] is False
    assert result["logs"] == []


# ============================================================
# save_alert()
# ============================================================

def test_save_alert(test_database):
    log_result = save_log_and_get_id({
        "timestamp": "2026-09-10 23:00:00",
        "level": "ERROR",
        "message": "Database failed",
        "category": "DATABASE_ERROR",
    })

    alert = {
        "log_id": log_result["log_id"],
        "level": "ERROR",
        "category": "DATABASE_ERROR",
        "message": "Database failed",
        "created_at": "2026-09-10 23:00:00",
    }

    result = save_alert(alert)

    assert result["success"] is True
    assert result["inserted"] is True
    assert isinstance(result["alert_id"], int)
    assert result["message"] == "Alert saved successfully."


def test_save_duplicate_alert(test_database):
    log_result = save_log_and_get_id({
        "timestamp": "2026-09-10 23:10:00",
        "level": "CRITICAL",
        "message": "Payment gateway failed",
        "category": "PAYMENT_ERROR",
    })

    alert = {
        "log_id": log_result["log_id"],
        "level": "CRITICAL",
        "category": "PAYMENT_ERROR",
        "message": "Payment gateway failed",
        "created_at": "2026-09-10 23:10:00",
    }

    first_result = save_alert(alert)
    second_result = save_alert(alert)

    assert first_result["success"] is True
    assert first_result["inserted"] is True

    assert second_result["success"] is True
    assert second_result["inserted"] is False
    assert second_result["alert_id"] == first_result["alert_id"]


def test_save_alert_invalid_input(test_database):
    result = save_alert(None)

    assert result["success"] is False
    assert result["message"] == "Invalid alert data."


# ============================================================
# get_all_alerts()
# ============================================================

def test_get_all_alerts(test_database):
    log_result = save_log_and_get_id({
        "timestamp": "2026-09-10 23:20:00",
        "level": "ERROR",
        "message": "API failed",
        "category": "API_ERROR",
    })

    save_alert({
        "log_id": log_result["log_id"],
        "level": "ERROR",
        "category": "API_ERROR",
        "message": "API failed",
        "created_at": "2026-09-10 23:20:00",
    })

    result = get_all_alerts()

    assert len(result) == 1
    assert result[0]["level"] == "ERROR"
    assert result[0]["category"] == "API_ERROR"


# ============================================================
# get_unacknowledged_alerts()
# ============================================================

def test_get_unacknowledged_alerts(test_database):
    log_result = save_log_and_get_id({
        "timestamp": "2026-09-10 23:30:00",
        "level": "ERROR",
        "message": "Network timeout",
        "category": "NETWORK_ERROR",
    })

    alert_result = save_alert({
        "log_id": log_result["log_id"],
        "level": "ERROR",
        "category": "NETWORK_ERROR",
        "message": "Network timeout",
        "created_at": "2026-09-10 23:30:00",
    })

    result = get_unacknowledged_alerts()

    assert len(result) == 1
    assert result[0]["id"] == alert_result["alert_id"]
    assert result[0]["acknowledged"] == 0


# ============================================================
# acknowledge_alert()
# ============================================================

def test_acknowledge_alert(test_database):
    log_result = save_log_and_get_id({
        "timestamp": "2026-09-10 23:40:00",
        "level": "CRITICAL",
        "message": "Payment gateway unavailable",
        "category": "PAYMENT_ERROR",
    })

    alert_result = save_alert({
        "log_id": log_result["log_id"],
        "level": "CRITICAL",
        "category": "PAYMENT_ERROR",
        "message": "Payment gateway unavailable",
        "created_at": "2026-09-10 23:40:00",
    })

    result = acknowledge_alert(alert_result["alert_id"])

    assert result["success"] is True
    assert result["updated"] is True
    assert result["message"] == "Alert acknowledged successfully."

    unacknowledged = get_unacknowledged_alerts()

    assert len(unacknowledged) == 0


def test_acknowledge_alert_not_found(test_database):
    result = acknowledge_alert(99999)

    assert result["success"] is False
    assert result["updated"] is False
    assert result["message"] == "Alert not found."


def test_acknowledge_alert_invalid_input(test_database):
    result = acknowledge_alert(None)

    assert result["success"] is False
    assert result["updated"] is False

    result = acknowledge_alert(0)

    assert result["success"] is False
    assert result["updated"] is False

    result = acknowledge_alert(True)

    assert result["success"] is False
    assert result["updated"] is False


# ============================================================
# save_log_and_get_id()
# ============================================================

def test_save_log_and_get_id(test_database):
    log = {
        "timestamp": "2026-09-10 23:50:00",
        "level": "ERROR",
        "message": "Database connection failed",
        "category": "DATABASE_ERROR",
    }

    result = save_log_and_get_id(log)

    assert result["success"] is True
    assert isinstance(result["log_id"], int)
    assert result["log_id"] > 0
    assert result["inserted"] is True
    assert result["message"] == "Log saved successfully."


def test_save_log_and_get_id_duplicate(test_database):
    log = {
        "timestamp": "2026-09-10 23:55:00",
        "level": "ERROR",
        "message": "Database connection failed",
        "category": "DATABASE_ERROR",
    }

    first_result = save_log_and_get_id(log)
    second_result = save_log_and_get_id(log)

    assert first_result["success"] is True
    assert first_result["inserted"] is True

    assert second_result["success"] is True
    assert second_result["inserted"] is False

    assert second_result["log_id"] == first_result["log_id"]
    assert second_result["message"] == "Log already exists."


def test_save_log_and_get_id_invalid_input(test_database):
    result = save_log_and_get_id(None)

    assert result["success"] is False
    assert result["log_id"] is None
    assert result["inserted"] is False
    assert result["message"] == "Invalid log data."


def test_save_log_and_get_id_invalid_fields(test_database):
    result = save_log_and_get_id({
        "timestamp": "invalid",
        "level": "ERROR",
        "message": "Something failed",
        "category": None,
    })

    assert result["success"] is False
    assert result["log_id"] is None
    assert result["inserted"] is False
    assert result["message"] == "Invalid timestamp."
