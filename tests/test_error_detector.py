from app.services.error_detector import (
    detect_error,
    classify_error
)


# ============================================================
# 1. DETECT ERROR LEVELS
# ============================================================

def test_detect_error_levels():

    logs = [
        {
            "timestamp": "2026-09-10 10:00:00",
            "level": "INFO",
            "message": "User logged in"
        },
        {
            "timestamp": "2026-09-10 10:01:00",
            "level": "WARNING",
            "message": "API is slow"
        },
        {
            "timestamp": "2026-09-10 10:02:00",
            "level": "ERROR",
            "message": "Database failed"
        },
        {
            "timestamp": "2026-09-10 10:03:00",
            "level": "CRITICAL",
            "message": "Payment gateway unavailable"
        }
    ]

    result = detect_error(logs)

    assert len(result) == 3
    assert result[0]["level"] == "WARNING"
    assert result[1]["level"] == "ERROR"
    assert result[2]["level"] == "CRITICAL"


# ============================================================
# 2. INFO SHOULD NOT BE ERROR
# ============================================================

def test_info_is_not_error():

    logs = [
        {
            "level": "INFO",
            "message": "Server started"
        }
    ]

    result = detect_error(logs)

    assert result == []


# ============================================================
# 3. NONE INPUT
# ============================================================

def test_detect_error_none():

    result = detect_error(None)

    assert result == []


# ============================================================
# 4. INVALID INPUT TYPE
# ============================================================

def test_detect_error_invalid_input():

    test_inputs = [
        "invalid",
        123,
        True,
        {},
    ]

    for value in test_inputs:

        result = detect_error(value)

        assert result == []


# ============================================================
# 5. MALFORMED LOG RECORDS
# ============================================================

def test_detect_error_malformed_records():

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
            "message": "Database failed"
        },
        {
            "level": "ERROR",
            "message": "Database failed"
        }
    ]

    result = detect_error(logs)

    assert len(result) == 1
    assert result[0]["level"] == "ERROR"


# ============================================================
# 6. LOWERCASE ERROR LEVEL
# ============================================================

def test_detect_error_lowercase_level():

    logs = [
        {
            "level": "error",
            "message": "Database failed"
        }
    ]

    result = detect_error(logs)

    assert len(result) == 1
    assert result[0]["level"] == "error"


# ============================================================
# 7. DATABASE ERROR
# ============================================================

def test_classify_database_error():

    log = {
        "level": "ERROR",
        "message": "Database connection failed"
    }

    result = classify_error(log)

    assert result == "DATABASE_ERROR"


# ============================================================
# 8. AUTHENTICATION ERROR
# ============================================================

def test_classify_authentication_error():

    log = {
        "level": "ERROR",
        "message": "Invalid username or password"
    }

    result = classify_error(log)

    assert result == "AUTHENTICATION_ERROR"


# ============================================================
# 9. NETWORK ERROR
# ============================================================

def test_classify_network_error():

    log = {
        "level": "ERROR",
        "message": "Network connection timeout"
    }

    result = classify_error(log)

    assert result == "NETWORK_ERROR"


# ============================================================
# 10. PAYMENT ERROR
# ============================================================

def test_classify_payment_error():

    log = {
        "level": "CRITICAL",
        "message": "Payment gateway is unavailable"
    }

    result = classify_error(log)

    assert result == "PAYMENT_ERROR"


# ============================================================
# 11. API ERROR
# ============================================================

def test_classify_api_error():

    log = {
        "level": "WARNING",
        "message": "API response time is slow"
    }

    result = classify_error(log)

    assert result == "API_ERROR"


# ============================================================
# 12. UNKNOWN ERROR
# ============================================================

def test_classify_unknown_error():

    log = {
        "level": "ERROR",
        "message": "Something unexpected happened"
    }

    result = classify_error(log)

    assert result == "UNKNOWN_ERROR"


# ============================================================
# 13. NONE LOG
# ============================================================

def test_classify_none_log():

    result = classify_error(None)

    assert result == "UNKNOWN_ERROR"


# ============================================================
# 14. INVALID LOG TYPE
# ============================================================

def test_classify_invalid_log_type():

    test_inputs = [
        "invalid",
        123,
        True,
        [],
        None
    ]

    for value in test_inputs:

        result = classify_error(value)

        assert result == "UNKNOWN_ERROR"


# ============================================================
# 15. MISSING MESSAGE
# ============================================================

def test_classify_missing_message():

    log = {
        "level": "ERROR"
    }

    result = classify_error(log)

    assert result == "UNKNOWN_ERROR"


# ============================================================
# 16. EMPTY MESSAGE
# ============================================================

def test_classify_empty_message():

    log = {
        "level": "ERROR",
        "message": "   "
    }

    result = classify_error(log)

    assert result == "UNKNOWN_ERROR"


# ============================================================
# 17. NON-STRING MESSAGE
# ============================================================

def test_classify_non_string_message():

    log = {
        "level": "ERROR",
        "message": 12345
    }

    result = classify_error(log)

    assert result == "UNKNOWN_ERROR"