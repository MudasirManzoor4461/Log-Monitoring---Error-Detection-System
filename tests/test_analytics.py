from app.services.analytics import (
    generate_analytics,
    generate_error_trends
)


# ============================================================
# 1. BASIC ANALYTICS
# ============================================================

def test_generate_analytics():

    logs = [
        {
            "timestamp": "2026-09-10 10:00:00",
            "level": "INFO",
            "message": "Server started"
        },
        {
            "timestamp": "2026-09-10 10:10:00",
            "level": "WARNING",
            "message": "API is slow",
            "category": "API_ERROR"
        },
        {
            "timestamp": "2026-09-10 10:20:00",
            "level": "ERROR",
            "message": "Database failed",
            "category": "DATABASE_ERROR"
        },
        {
            "timestamp": "2026-09-10 10:30:00",
            "level": "CRITICAL",
            "message": "Payment failed",
            "category": "PAYMENT_ERROR"
        }
    ]

    result = generate_analytics(logs)

    assert result["success"] is True
    assert result["total_logs"] == 4
    assert result["total_errors"] == 3
    assert result["total_warnings"] == 1
    assert result["total_critical"] == 1

    assert result["logs_by_level"]["INFO"] == 1
    assert result["logs_by_level"]["WARNING"] == 1
    assert result["logs_by_level"]["ERROR"] == 1
    assert result["logs_by_level"]["CRITICAL"] == 1

    assert result["errors_by_category"]["API_ERROR"] == 1
    assert result["errors_by_category"]["DATABASE_ERROR"] == 1
    assert result["errors_by_category"]["PAYMENT_ERROR"] == 1

    assert result["error_rate"] == 75.0


# ============================================================
# 2. MOST COMMON ERROR
# ============================================================

def test_most_common_error():

    logs = [
        {
            "level": "ERROR",
            "category": "DATABASE_ERROR"
        },
        {
            "level": "ERROR",
            "category": "DATABASE_ERROR"
        },
        {
            "level": "CRITICAL",
            "category": "PAYMENT_ERROR"
        }
    ]

    result = generate_analytics(logs)

    assert result["most_common_error"] == "DATABASE_ERROR"


# ============================================================
# 3. EMPTY INPUT
# ============================================================

def test_generate_analytics_empty():

    result = generate_analytics([])

    assert result["success"] is True
    assert result["total_logs"] == 0
    assert result["total_errors"] == 0
    assert result["total_warnings"] == 0
    assert result["total_critical"] == 0
    assert result["logs_by_level"] == {}
    assert result["errors_by_category"] == {}
    assert result["most_common_error"] is None
    assert result["error_rate"] == 0.0


# ============================================================
# 4. NONE INPUT
# ============================================================

def test_generate_analytics_none():

    result = generate_analytics(None)

    assert result["success"] is True
    assert result["total_logs"] == 0
    assert result["error_rate"] == 0.0


# ============================================================
# 5. INVALID INPUT TYPE
# ============================================================

def test_generate_analytics_invalid_input():

    test_inputs = [
        "invalid",
        123,
        True,
        {},
    ]

    for value in test_inputs:

        result = generate_analytics(value)

        assert result["success"] is False
        assert result["total_logs"] == 0
        assert result["total_errors"] == 0


# ============================================================
# 6. MALFORMED LOG RECORDS
# ============================================================

def test_generate_analytics_malformed_records():

    logs = [
        None,
        "invalid",
        123,
        {},
        {
            "message": "Database failed"
        },
        {
            "level": 123,
            "message": "Invalid level"
        },
        {
            "level": "ERROR",
            "category": "DATABASE_ERROR"
        }
    ]

    result = generate_analytics(logs)

    assert result["success"] is True
    assert result["total_logs"] == 1
    assert result["total_errors"] == 1
    assert result["errors_by_category"]["DATABASE_ERROR"] == 1


# ============================================================
# 7. UNKNOWN CATEGORY
# ============================================================

def test_generate_analytics_without_category():

    logs = [
        {
            "level": "ERROR",
            "message": "Something failed"
        }
    ]

    result = generate_analytics(logs)

    assert result["success"] is True
    assert result["total_logs"] == 1
    assert result["total_errors"] == 1
    assert result["errors_by_category"] == {}


# ============================================================
# 8. ERROR RATE
# ============================================================

def test_error_rate():

    logs = [
        {"level": "INFO"},
        {"level": "INFO"},
        {"level": "ERROR"},
        {"level": "ERROR"},
        {"level": "CRITICAL"},
    ]

    result = generate_analytics(logs)

    assert result["total_logs"] == 5
    assert result["total_errors"] == 3
    assert result["error_rate"] == 60.0


# ============================================================
# 9. ERROR TRENDS
# ============================================================

def test_generate_error_trends():

    logs = [
        {
            "timestamp": "2026-09-10 10:05:00",
            "level": "ERROR"
        },
        {
            "timestamp": "2026-09-10 10:20:00",
            "level": "CRITICAL"
        },
        {
            "timestamp": "2026-09-10 11:10:00",
            "level": "WARNING"
        },
        {
            "timestamp": "2026-09-10 11:30:00",
            "level": "INFO"
        }
    ]

    result = generate_error_trends(logs)

    assert len(result) == 2

    assert result[0]["time"] == "2026-09-10 10:00:00"
    assert result[0]["error_count"] == 2

    assert result[1]["time"] == "2026-09-10 11:00:00"
    assert result[1]["error_count"] == 1


# ============================================================
# 10. ERROR TRENDS EMPTY INPUT
# ============================================================

def test_generate_error_trends_empty():

    result = generate_error_trends([])

    assert result == []


# ============================================================
# 11. ERROR TRENDS NONE
# ============================================================

def test_generate_error_trends_none():

    result = generate_error_trends(None)

    assert result == []


# ============================================================
# 12. ERROR TRENDS INVALID INPUT
# ============================================================

def test_generate_error_trends_invalid_input():

    test_inputs = [
        "invalid",
        123,
        True,
        {},
    ]

    for value in test_inputs:

        result = generate_error_trends(value)

        assert result == []


# ============================================================
# 13. ERROR TRENDS INVALID RECORDS
# ============================================================

def test_generate_error_trends_invalid_records():

    logs = [
        None,
        "invalid",
        {},
        {
            "level": "ERROR"
        },
        {
            "timestamp": "invalid",
            "level": "ERROR"
        },
        {
            "timestamp": "2026-09-10 10:00:00",
            "level": "INFO"
        }
    ]

    result = generate_error_trends(logs)

    assert result == []