from app.services.error_grouper import group_errors


# ============================================================
# 1. GROUP ERRORS BY CATEGORY
# ============================================================

def test_group_errors_by_category():

    logs = [
        {
            "timestamp": "2026-09-10 10:00:00",
            "level": "ERROR",
            "message": "Database failed",
            "category": "DATABASE_ERROR"
        },
        {
            "timestamp": "2026-09-10 10:05:00",
            "level": "ERROR",
            "message": "Another database failure",
            "category": "DATABASE_ERROR"
        },
        {
            "timestamp": "2026-09-10 11:00:00",
            "level": "CRITICAL",
            "message": "Payment failed",
            "category": "PAYMENT_ERROR"
        }
    ]

    result = group_errors(logs)

    assert "DATABASE_ERROR" in result
    assert "PAYMENT_ERROR" in result

    assert result["DATABASE_ERROR"]["count"] == 2
    assert result["PAYMENT_ERROR"]["count"] == 1


# ============================================================
# 2. FIRST SEEN AND LAST SEEN
# ============================================================

def test_group_errors_first_and_last_seen():

    logs = [
        {
            "timestamp": "2026-09-10 10:00:00",
            "level": "ERROR",
            "message": "Database failed",
            "category": "DATABASE_ERROR"
        },
        {
            "timestamp": "2026-09-10 12:30:00",
            "level": "ERROR",
            "message": "Database failed again",
            "category": "DATABASE_ERROR"
        }
    ]

    result = group_errors(logs)

    assert result["DATABASE_ERROR"]["first_seen"] == (
        "2026-09-10 10:00:00"
    )

    assert result["DATABASE_ERROR"]["last_seen"] == (
        "2026-09-10 12:30:00"
    )


# ============================================================
# 3. NONE INPUT
# ============================================================

def test_group_errors_none():

    result = group_errors(None)

    assert result == {}


# ============================================================
# 4. INVALID INPUT TYPE
# ============================================================

def test_group_errors_invalid_input():

    test_inputs = [
        "invalid",
        123,
        True,
        {},
    ]

    for value in test_inputs:

        result = group_errors(value)

        assert result == {}


# ============================================================
# 5. MALFORMED RECORDS
# ============================================================

def test_group_errors_malformed_records():

    logs = [
        None,
        "invalid",
        123,
        {},
        {
            "category": "DATABASE_ERROR"
        },
        {
            "timestamp": "invalid",
            "category": "DATABASE_ERROR"
        },
        {
            "timestamp": "2026-09-10 10:00:00",
            "category": "DATABASE_ERROR"
        }
    ]

    result = group_errors(logs)

    assert "DATABASE_ERROR" in result
    assert result["DATABASE_ERROR"]["count"] == 1


# ============================================================
# 6. MISSING CATEGORY
# ============================================================

def test_group_errors_missing_category():

    logs = [
        {
            "timestamp": "2026-09-10 10:00:00",
            "level": "ERROR",
            "message": "Something failed"
        }
    ]

    result = group_errors(logs)

    assert "UNKNOWN_ERROR" in result
    assert result["UNKNOWN_ERROR"]["count"] == 1


# ============================================================
# 7. EMPTY CATEGORY
# ============================================================

def test_group_errors_empty_category():

    logs = [
        {
            "timestamp": "2026-09-10 10:00:00",
            "level": "ERROR",
            "message": "Something failed",
            "category": "   "
        }
    ]

    result = group_errors(logs)

    assert "UNKNOWN_ERROR" in result
    assert result["UNKNOWN_ERROR"]["count"] == 1


# ============================================================
# 8. INVALID CATEGORY TYPE
# ============================================================

def test_group_errors_invalid_category_type():

    logs = [
        {
            "timestamp": "2026-09-10 10:00:00",
            "level": "ERROR",
            "message": "Something failed",
            "category": 123
        }
    ]

    result = group_errors(logs)

    assert "UNKNOWN_ERROR" in result


# ============================================================
# 9. INVALID TIMESTAMP
# ============================================================

def test_group_errors_invalid_timestamp():

    logs = [
        {
            "timestamp": "2026-99-99 10:00:00",
            "level": "ERROR",
            "message": "Database failed",
            "category": "DATABASE_ERROR"
        }
    ]

    result = group_errors(logs)

    assert result == {}


# ============================================================
# 10. MISSING TIMESTAMP
# ============================================================

def test_group_errors_missing_timestamp():

    logs = [
        {
            "level": "ERROR",
            "message": "Database failed",
            "category": "DATABASE_ERROR"
        }
    ]

    result = group_errors(logs)

    assert result == {}


# ============================================================
# 11. MULTIPLE CATEGORIES
# ============================================================

def test_group_errors_multiple_categories():

    logs = [
        {
            "timestamp": "2026-09-10 10:00:00",
            "category": "DATABASE_ERROR"
        },
        {
            "timestamp": "2026-09-10 10:01:00",
            "category": "PAYMENT_ERROR"
        },
        {
            "timestamp": "2026-09-10 10:02:00",
            "category": "NETWORK_ERROR"
        }
    ]

    result = group_errors(logs)

    assert len(result) == 3
    assert result["DATABASE_ERROR"]["count"] == 1
    assert result["PAYMENT_ERROR"]["count"] == 1
    assert result["NETWORK_ERROR"]["count"] == 1