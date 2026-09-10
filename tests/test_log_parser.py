from app.services.log_parser import parse_log_line, parse_log_file


# ============================================================
# 1. VALID LOG LINE
# ============================================================

def test_parse_valid_log_line():
    line = (
        "2026-09-10 16:00:00 "
        "ERROR Database connection failed"
    )

    result = parse_log_line(line)

    assert result is not None
    assert result["timestamp"] == "2026-09-10 16:00:00"
    assert result["level"] == "ERROR"
    assert result["message"] == "Database connection failed"


# ============================================================
# 2. INVALID LOG LINE
# ============================================================

def test_parse_invalid_log_line():
    line = "this is completely invalid"

    result = parse_log_line(line)

    assert result is None


# ============================================================
# 3. EMPTY LOG LINE
# ============================================================

def test_parse_empty_log_line():
    result = parse_log_line("")

    assert result is None


# ============================================================
# 4. WHITESPACE ONLY
# ============================================================

def test_parse_whitespace_log_line():
    result = parse_log_line("     ")

    assert result is None


# ============================================================
# 5. INVALID DATE
# ============================================================

def test_parse_invalid_date():
    line = (
        "2026-99-99 10:02:00 "
        "ERROR Invalid date"
    )

    result = parse_log_line(line)

    assert result is None


# ============================================================
# 6. MISSING TIME
# ============================================================

def test_parse_missing_time():
    line = (
        "2026-09-08 ERROR "
        "Missing time"
    )

    result = parse_log_line(line)

    assert result is None


# ============================================================
# 7. UNKNOWN LOG LEVEL
# ============================================================

def test_parse_unknown_log_level():
    line = (
        "2026-09-08 10:03:00 "
        "UNKNOWN Unknown log level"
    )

    result = parse_log_line(line)

    assert result is None


# ============================================================
# 8. MISSING MESSAGE
# ============================================================

def test_parse_missing_message():
    line = (
        "2026-09-08 10:04:00 "
        "WARNING"
    )

    result = parse_log_line(line)

    assert result is None


# ============================================================
# 9. ALL VALID LOG LEVELS
# ============================================================

def test_parse_all_valid_log_levels():

    levels = [
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL"
    ]

    for level in levels:

        line = (
            f"2026-09-10 16:00:00 "
            f"{level} Test message"
        )

        result = parse_log_line(line)

        assert result is not None
        assert result["level"] == level


# ============================================================
# 10. LOG LEVEL CASE HANDLING
# ============================================================

def test_parse_lowercase_log_level():

    line = (
        "2026-09-10 16:00:00 "
        "error Database connection failed"
    )

    result = parse_log_line(line)

    assert result is not None
    assert result["level"] == "ERROR"


# ============================================================
# 11. MESSAGE WITH SPACES
# ============================================================

def test_parse_message_with_spaces():

    line = (
        "2026-09-10 16:00:00 "
        "ERROR Database connection "
        "failed because server is unavailable"
    )

    result = parse_log_line(line)

    assert result is not None
    assert result["message"] == (
        "Database connection failed because "
        "server is unavailable"
    )


# ============================================================
# 12. NON-STRING INPUT
# ============================================================

def test_parse_non_string_input():

    test_inputs = [
        None,
        123,
        True,
        [],
        {},
    ]

    for value in test_inputs:

        result = parse_log_line(value)

        assert result is None


# ============================================================
# 13. EXTRA SPACES
# ============================================================

def test_parse_log_line_with_extra_spaces():

    line = (
        "   2026-09-10 16:00:00 "
        "ERROR Database connection failed   "
    )

    result = parse_log_line(line)

    assert result is not None
    assert result["level"] == "ERROR"
    assert result["message"] == "Database connection failed"


# ============================================================
# 14. VALID LOG FILE
# ============================================================

def test_parse_log_file():

    logs = parse_log_file(
        "sample_logs/app.log"
    )

    assert isinstance(logs, list)
    assert len(logs) > 0

    for log in logs:

        assert "timestamp" in log
        assert "level" in log
        assert "message" in log


# ============================================================
# 15. INVALID FILE PATH
# ============================================================

def test_parse_log_file_invalid_path():

    logs = parse_log_file(
        "sample_logs/file_that_does_not_exist.log"
    )

    assert logs == []


# ============================================================
# 16. INVALID FILE PATH TYPE
# ============================================================

def test_parse_log_file_invalid_path_type():

    test_inputs = [
        None,
        123,
        True,
        [],
        {},
    ]

    for value in test_inputs:

        logs = parse_log_file(value)

        assert logs == []