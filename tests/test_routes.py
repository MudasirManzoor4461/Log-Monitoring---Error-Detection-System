from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


# ============================================================
# Health
# ============================================================

def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "log-monitoring-system"


# ============================================================
# GET /logs
# ============================================================

def test_get_logs_without_filters():
    fake_logs = [
        {
            "id": 1,
            "timestamp": "2026-09-10 10:00:00",
            "level": "INFO",
            "message": "Server started",
            "category": None,
        }
    ]

    with patch(
        "app.api.routes.get_all_logs",
        return_value=fake_logs,
    ):
        response = client.get("/logs")

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["count"] == 1
    assert data["total_logs"] == 1
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total_pages"] == 1
    assert len(data["logs"]) == 1
    assert data["logs"][0]["id"] == 1


def test_get_logs_by_level():
    fake_logs = [
        {
            "id": 2,
            "timestamp": "2026-09-10 10:01:00",
            "level": "ERROR",
            "message": "Database failed",
            "category": "DATABASE_ERROR",
        }
    ]

    with patch(
        "app.api.routes.get_logs_by_level",
        return_value=fake_logs,
    ):
        response = client.get("/logs?level=error")

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["count"] == 1
    assert data["logs"][0]["level"] == "ERROR"


def test_get_logs_by_category():
    fake_logs = [
        {
            "id": 3,
            "timestamp": "2026-09-10 10:02:00",
            "level": "ERROR",
            "message": "Database failed",
            "category": "DATABASE_ERROR",
        }
    ]

    with patch(
        "app.api.routes.get_logs_by_category",
        return_value=fake_logs,
    ):
        response = client.get(
            "/logs?category=DATABASE_ERROR"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["count"] == 1
    assert data["logs"][0]["category"] == "DATABASE_ERROR"


def test_get_logs_by_level_and_category():
    fake_logs = [
        {
            "id": 4,
            "timestamp": "2026-09-10 10:03:00",
            "level": "ERROR",
            "message": "Database failed",
            "category": "DATABASE_ERROR",
        },
        {
            "id": 5,
            "timestamp": "2026-09-10 10:04:00",
            "level": "ERROR",
            "message": "API failed",
            "category": "API_ERROR",
        },
    ]

    with patch(
        "app.api.routes.get_logs_by_level",
        return_value=fake_logs,
    ):
        response = client.get(
            "/logs?level=ERROR&category=DATABASE_ERROR"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 1
    assert data["logs"][0]["category"] == "DATABASE_ERROR"


def test_get_logs_invalid_level():
    response = client.get("/logs?level=DEBUG")

    assert response.status_code == 400
    assert "Invalid log level" in response.json()["detail"]


def test_get_logs_empty_category():
    response = client.get("/logs?category=%20%20")

    assert response.status_code == 400
    assert response.json()["detail"] == "Category cannot be empty."


def test_get_logs_pagination():
    fake_logs = []

    for number in range(1, 6):
        fake_logs.append({
            "id": number,
            "timestamp": f"2026-09-10 11:0{number}:00",
            "level": "INFO",
            "message": f"Log {number}",
            "category": None,
        })

    with patch(
        "app.api.routes.get_all_logs",
        return_value=fake_logs,
    ):
        response = client.get(
            "/logs?page=2&page_size=2"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["total_logs"] == 5
    assert data["page"] == 2
    assert data["page_size"] == 2
    assert data["total_pages"] == 3
    assert data["count"] == 2


# ============================================================
# GET /logs/errors
# ============================================================

def test_get_error_logs():
    fake_logs = [
        {
            "id": 10,
            "timestamp": "2026-09-10 12:00:00",
            "level": "INFO",
            "message": "Server started",
            "category": None,
        },
        {
            "id": 11,
            "timestamp": "2026-09-10 12:01:00",
            "level": "ERROR",
            "message": "Database failed",
            "category": "DATABASE_ERROR",
        },
    ]

    with patch(
        "app.api.routes.get_all_logs",
        return_value=fake_logs,
    ):
        response = client.get("/logs/errors")

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["count"] == 1
    assert data["errors"][0]["level"] == "ERROR"


# ============================================================
# GET /errors
# ============================================================

def test_get_errors():
    fake_logs = [
        {
            "id": 20,
            "timestamp": "2026-09-10 13:00:00",
            "level": "WARNING",
            "message": "Slow API response",
            "category": "API_ERROR",
        }
    ]

    with patch(
        "app.api.routes.get_all_logs",
        return_value=fake_logs,
    ):
        response = client.get("/errors")

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["count"] == 1
    assert data["errors"][0]["level"] == "WARNING"


# ============================================================
# GET /errors/top
# ============================================================

def test_get_top_errors():
    fake_logs = [
        {
            "id": 30,
            "timestamp": "2026-09-10 14:00:00",
            "level": "ERROR",
            "message": "Database connection failed",
            "category": None,
        },
        {
            "id": 31,
            "timestamp": "2026-09-10 14:01:00",
            "level": "ERROR",
            "message": "Database timeout",
            "category": None,
        },
    ]

    with patch(
        "app.api.routes.get_all_logs",
        return_value=fake_logs,
    ):
        response = client.get("/errors/top")

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["count"] == 1
    assert data["errors"][0]["category"] == "DATABASE_ERROR"
    assert data["errors"][0]["count"] == 2


# ============================================================
# GET /analytics
# ============================================================

def test_analytics():
    fake_logs = [
        {
            "id": 40,
            "timestamp": "2026-09-10 15:00:00",
            "level": "INFO",
            "message": "Server started",
            "category": None,
        },
        {
            "id": 41,
            "timestamp": "2026-09-10 15:01:00",
            "level": "ERROR",
            "message": "Database failed",
            "category": None,
        },
        {
            "id": 42,
            "timestamp": "2026-09-10 15:02:00",
            "level": "CRITICAL",
            "message": "Payment gateway failed",
            "category": None,
        },
    ]

    with patch(
        "app.api.routes.get_all_logs",
        return_value=fake_logs,
    ):
        response = client.get("/analytics")

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["total_logs"] == 3
    assert data["total_errors"] == 2
    assert data["total_critical"] == 1
    assert data["error_rate"] == 66.67


# ============================================================
# GET /analytics/trends
# ============================================================

def test_error_trends():
    fake_logs = [
        {
            "id": 50,
            "timestamp": "2026-09-10 16:10:00",
            "level": "ERROR",
            "message": "Database failed",
            "category": "DATABASE_ERROR",
        },
        {
            "id": 51,
            "timestamp": "2026-09-10 16:20:00",
            "level": "CRITICAL",
            "message": "Payment failed",
            "category": "PAYMENT_ERROR",
        },
    ]

    with patch(
        "app.api.routes.get_all_logs",
        return_value=fake_logs,
    ):
        response = client.get("/analytics/trends")

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["count"] == 1
    assert data["trends"][0]["error_count"] == 2


# ============================================================
# GET /logs/search
# ============================================================

def test_search_logs():
    fake_result = {
        "success": True,
        "logs": [
            {
                "id": 60,
                "timestamp": "2026-09-10 17:00:00",
                "level": "ERROR",
                "message": "Database connection failed",
                "category": "DATABASE_ERROR",
            }
        ],
        "total_logs": 1,
        "page": 1,
        "page_size": 10,
        "total_pages": 1,
        "has_next": False,
        "has_previous": False,
    }

    with patch(
        "app.api.routes.search_logs_by_message",
        return_value=fake_result,
    ):
        response = client.get(
            "/logs/search?q=database"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["total_logs"] == 1
    assert data["logs"][0]["message"] == "Database connection failed"


def test_search_logs_empty_query():
    response = client.get("/logs/search?q=%20%20")

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Search query cannot be empty."
    )


def test_search_logs_missing_query():
    response = client.get("/logs/search")

    assert response.status_code == 422


# ============================================================
# GET /logs/time-range
# ============================================================

def test_logs_by_time_range():
    fake_logs = [
        {
            "id": 70,
            "timestamp": "2026-09-10 18:00:00",
            "level": "ERROR",
            "message": "Database failed",
            "category": "DATABASE_ERROR",
        }
    ]

    with patch(
        "app.api.routes.get_logs_by_time_range",
        return_value=fake_logs,
    ):
        response = client.get(
            "/logs/time-range"
            "?start_time=2026-09-10%2017:00:00"
            "&end_time=2026-09-10%2019:00:00"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["count"] == 1
    assert data["start_time"] == "2026-09-10T17:00:00"
    assert data["end_time"] == "2026-09-10T19:00:00"


def test_logs_by_time_range_invalid_timestamp():
    response = client.get(
        "/logs/time-range"
        "?start_time=invalid"
        "&end_time=2026-09-10%2019:00:00"
    )

    assert response.status_code == 400
    assert "Invalid timestamp format" in response.json()["detail"]


def test_logs_by_time_range_wrong_order():
    response = client.get(
        "/logs/time-range"
        "?start_time=2026-09-10%2019:00:00"
        "&end_time=2026-09-10%2017:00:00"
    )

    assert response.status_code == 400
    assert "start_time cannot be greater" in response.json()["detail"]


# ============================================================
# DELETE /logs/{log_id}
# ============================================================

def test_delete_log():
    fake_result = {
        "success": True,
        "deleted": True,
        "message": "Log deleted successfully.",
    }

    with patch(
        "app.api.routes.delete_log_by_id",
        return_value=fake_result,
    ):
        response = client.delete("/logs/100")

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["deleted"] is True


def test_delete_log_not_found():
    fake_result = {
        "success": False,
        "deleted": False,
        "message": "Log not found.",
    }

    with patch(
        "app.api.routes.delete_log_by_id",
        return_value=fake_result,
    ):
        response = client.delete("/logs/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Log not found."


def test_delete_log_invalid_id():
    response = client.delete("/logs/abc")

    assert response.status_code == 422


# ============================================================
# POST /logs/ingest
# ============================================================

def test_ingest_logs():
    fake_logs = [
        {
            "timestamp": "2026-09-10 20:00:00",
            "level": "INFO",
            "message": "Server started",
        },
        {
            "timestamp": "2026-09-10 20:01:00",
            "level": "ERROR",
            "message": "Database failed",
        },
    ]

    fake_save_result = {
        "success": True,
        "inserted_logs": 2,
        "duplicate_logs": 0,
        "skipped_logs": 0,
    }

    with patch(
        "app.api.routes.Path.exists",
        return_value=True,
    ):
        with patch(
            "app.api.routes.Path.is_file",
            return_value=True,
        ):
            with patch(
                "app.api.routes.parse_log_file",
                return_value=fake_logs,
            ):
                with patch(
                    "app.api.routes.save_logs",
                    return_value=fake_save_result,
                ):
                    response = client.post(
                        "/logs/ingest"
                        "?file_path=sample_logs/app.log"
                    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["parsed_logs"] == 2
    assert data["detected_errors"] == 1
    assert data["saved"]["inserted_logs"] == 2


def test_ingest_logs_missing_file():
    with patch(
        "app.api.routes.Path.exists",
        return_value=False,
    ):
        response = client.post(
            "/logs/ingest"
            "?file_path=sample_logs/missing.log"
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Log file not found."


def test_ingest_logs_empty_path():
    response = client.post(
        "/logs/ingest?file_path=%20%20"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "File path cannot be empty."
    )


# ============================================================
# GET /alerts
# ============================================================

def test_get_alerts():
    fake_alerts = [
        {
            "id": 1,
            "log_id": 100,
            "level": "ERROR",
            "category": "DATABASE_ERROR",
            "message": "Database failed",
            "created_at": "2026-09-10 21:00:00",
            "acknowledged": 0,
        }
    ]

    with patch(
        "app.api.routes.get_all_alerts",
        return_value=fake_alerts,
    ):
        response = client.get("/alerts")

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["count"] == 1
    assert data["alerts"][0]["id"] == 1
    assert data["alerts"][0]["acknowledged"] is False


# ============================================================
# GET /alerts/unacknowledged
# ============================================================

def test_get_unacknowledged_alerts():
    fake_alerts = [
        {
            "id": 2,
            "log_id": 101,
            "level": "CRITICAL",
            "category": "PAYMENT_ERROR",
            "message": "Payment failed",
            "created_at": "2026-09-10 21:10:00",
            "acknowledged": 0,
        }
    ]

    with patch(
        "app.api.routes.get_unacknowledged_alerts",
        return_value=fake_alerts,
    ):
        response = client.get(
            "/alerts/unacknowledged"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["count"] == 1
    assert data["alerts"][0]["acknowledged"] is False


# ============================================================
# PATCH /alerts/{alert_id}/acknowledge
# ============================================================

def test_acknowledge_alert():
    fake_result = {
        "success": True,
        "updated": True,
        "message": "Alert acknowledged successfully.",
    }

    with patch(
        "app.api.routes.acknowledge_alert",
        return_value=fake_result,
    ):
        response = client.patch(
            "/alerts/1/acknowledge"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["acknowledged"] is True
    assert data["message"] == (
        "Alert acknowledged successfully."
    )


def test_acknowledge_alert_not_found():
    fake_result = {
        "success": False,
        "updated": False,
        "message": "Alert not found.",
    }

    with patch(
        "app.api.routes.acknowledge_alert",
        return_value=fake_result,
    ):
        response = client.patch(
            "/alerts/99999/acknowledge"
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Alert not found."


def test_acknowledge_alert_invalid_id():
    response = client.patch(
        "/alerts/abc/acknowledge"
    )

    assert response.status_code == 422


def test_ingest_logs_path_traversal_blocked():
    response = client.post(
        "/logs/ingest?file_path=../logs.db"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "File path must be inside the sample_logs directory."
    )


def test_ingest_logs_absolute_path_blocked():
    response = client.post(
        "/logs/ingest"
        "?file_path=C:/Users/IT%20Computers/Downloads/log-monitoring-system/logs.db"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Absolute file paths are not allowed."
    )