from unittest.mock import patch

from app.services.live_monitor import process_new_log_line


def test_process_valid_info_log():
    line = "2026-09-10 17:00:00 INFO User logged in"

    with patch(
        "app.services.live_monitor.save_log_and_get_id",
        return_value={
            "success": True,
            "log_id": 1001,
            "inserted": True,
            "message": "Log saved successfully."
        }
    ):
        result = process_new_log_line(line)

    assert result["success"] is True
    assert result["log_id"] == 1001
    assert result["is_error"] is False
    assert result["category"] is None
    assert result["alert"]["alert"] is False
    assert result["saved_alert"] is None


def test_process_error_log():
    line = "2026-09-10 17:05:00 ERROR Database connection failed"

    with patch(
        "app.services.live_monitor.save_log_and_get_id",
        return_value={
            "success": True,
            "log_id": 1002,
            "inserted": True,
            "message": "Log saved successfully."
        }
    ):
        with patch(
            "app.services.live_monitor.save_alert",
            return_value={
                "success": True,
                "alert_id": 2001,
                "inserted": True,
                "message": "Alert saved successfully."
            }
        ):
            result = process_new_log_line(line)

    assert result["success"] is True
    assert result["log_id"] == 1002
    assert result["is_error"] is True
    assert result["category"] == "DATABASE_ERROR"
    assert result["alert"]["alert"] is True
    assert result["saved_alert"]["success"] is True


def test_process_critical_payment_error():
    line = "2026-09-10 17:10:00 CRITICAL Payment gateway is unavailable"

    with patch(
        "app.services.live_monitor.save_log_and_get_id",
        return_value={
            "success": True,
            "log_id": 1003,
            "inserted": True,
            "message": "Log saved successfully."
        }
    ):
        with patch(
            "app.services.live_monitor.save_alert",
            return_value={
                "success": True,
                "alert_id": 2002,
                "inserted": True,
                "message": "Alert saved successfully."
            }
        ):
            result = process_new_log_line(line)

    assert result["success"] is True
    assert result["category"] == "PAYMENT_ERROR"
    assert result["alert"]["level"] == "CRITICAL"
    assert result["saved_alert"]["alert_id"] == 2002


def test_process_invalid_log_line():
    result = process_new_log_line("this is completely invalid")

    assert result["success"] is False
    assert result["message"] == "Invalid log format."


def test_process_empty_log_line():
    result = process_new_log_line("")

    assert result["success"] is False
    assert result["message"] == "Log line cannot be empty."


def test_process_none_input():
    result = process_new_log_line(None)

    assert result["success"] is False
    assert result["message"] == "Invalid log line."


def test_process_invalid_input_types():
    for value in [123, True, [], {}]:
        result = process_new_log_line(value)

        assert result["success"] is False
        assert result["message"] == "Invalid log line."


def test_process_database_failure():
    line = "2026-09-10 17:20:00 ERROR Database connection failed"

    with patch(
        "app.services.live_monitor.save_log_and_get_id",
        return_value={
            "success": False,
            "message": "Database error."
        }
    ):
        result = process_new_log_line(line)

    assert result["success"] is False
    assert result["message"] == "Database error."


def test_process_invalid_database_response():
    line = "2026-09-10 17:25:00 ERROR Database connection failed"

    with patch(
        "app.services.live_monitor.save_log_and_get_id",
        return_value=None
    ):
        result = process_new_log_line(line)

    assert result["success"] is False
    assert result["message"] == "Unexpected database response."


def test_process_invalid_log_id():
    line = "2026-09-10 17:30:00 ERROR Database connection failed"

    with patch(
        "app.services.live_monitor.save_log_and_get_id",
        return_value={
            "success": True,
            "log_id": "invalid",
            "inserted": True
        }
    ):
        result = process_new_log_line(line)

    assert result["success"] is False
    assert result["message"] == "Invalid log ID returned by database."


def test_process_alert_save_failure():
    line = "2026-09-10 17:35:00 CRITICAL Payment gateway failed"

    with patch(
        "app.services.live_monitor.save_log_and_get_id",
        return_value={
            "success": True,
            "log_id": 1004,
            "inserted": True
        }
    ):
        with patch(
            "app.services.live_monitor.save_alert",
            return_value={
                "success": False,
                "message": "Unable to save alert."
            }
        ):
            result = process_new_log_line(line)

    assert result["success"] is False
    assert result["message"] == "Unable to save alert."