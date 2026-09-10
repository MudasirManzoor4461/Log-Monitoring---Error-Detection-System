from app.services.alert_service import generate_alert


def test_generate_alert_error():
    log = {
        "level": "ERROR",
        "message": "Database connection failed"
    }

    result = generate_alert(log)

    assert result["success"] is True
    assert result["alert"] is True
    assert result["level"] == "ERROR"
    assert result["message"] == "ERROR ALERT: Database connection failed"


def test_generate_alert_critical():
    log = {
        "level": "CRITICAL",
        "message": "Payment gateway is unavailable"
    }

    result = generate_alert(log)

    assert result["success"] is True
    assert result["alert"] is True
    assert result["level"] == "CRITICAL"
    assert result["message"] == "CRITICAL ALERT: Payment gateway is unavailable"


def test_generate_alert_info():
    log = {
        "level": "INFO",
        "message": "User logged in"
    }

    result = generate_alert(log)

    assert result["success"] is True
    assert result["alert"] is False
    assert result["message"] == "No alert required."


def test_generate_alert_warning():
    log = {
        "level": "WARNING",
        "message": "API response is slow"
    }

    result = generate_alert(log)

    assert result["success"] is True
    assert result["alert"] is False
    assert result["message"] == "No alert required."


def test_generate_alert_invalid_log():
    result = generate_alert(None)

    assert result["success"] is False
    assert result["alert"] is False
    assert result["message"] == "Invalid log record."


def test_generate_alert_invalid_level_type():
    log = {
        "level": 123,
        "message": "Something failed"
    }

    result = generate_alert(log)

    assert result["success"] is False
    assert result["alert"] is False
    assert result["message"] == "Invalid log level."


def test_generate_alert_empty_level():
    log = {
        "level": "   ",
        "message": "Something failed"
    }

    result = generate_alert(log)

    assert result["success"] is False
    assert result["alert"] is False
    assert result["message"] == "Log level cannot be empty."


def test_generate_alert_unknown_level():
    log = {
        "level": "DEBUG",
        "message": "Debug message"
    }

    result = generate_alert(log)

    assert result["success"] is False
    assert result["alert"] is False
    assert result["message"] == "Unknown log level."


def test_generate_alert_missing_message():
    log = {
        "level": "ERROR"
    }

    result = generate_alert(log)

    assert result["success"] is True
    assert result["alert"] is True
    assert result["message"] == "ERROR ALERT: No error message provided."


def test_generate_alert_none_message():
    log = {
        "level": "ERROR",
        "message": None
    }

    result = generate_alert(log)

    assert result["success"] is True
    assert result["alert"] is True
    assert result["message"] == "ERROR ALERT: No error message provided."

def test_generate_alert_empty_message():
    log = {
        "level": "ERROR",
        "message": "   "
    }

    result = generate_alert(log)

    assert result["success"] is True
    assert result["alert"] is True
    assert result["message"] == "ERROR ALERT: "
    

def test_generate_alert_lowercase_error():
    log = {
        "level": "error",
        "message": "Database connection failed"
    }

    result = generate_alert(log)

    assert result["success"] is True
    assert result["alert"] is True
    assert result["level"] == "ERROR"


def test_generate_alert_lowercase_critical():
    log = {
        "level": "critical",
        "message": "Payment gateway failed"
    }

    result = generate_alert(log)

    assert result["success"] is True
    assert result["alert"] is True
    assert result["level"] == "CRITICAL"


def test_generate_alert_level_with_spaces():
    log = {
        "level": "  ERROR  ",
        "message": "Database connection failed"
    }

    result = generate_alert(log)

    assert result["success"] is True
    assert result["alert"] is True
    assert result["level"] == "ERROR"


def test_generate_alert_invalid_input_types():
    for value in [123, True, [], "ERROR", None]:
        result = generate_alert(value)

        assert result["success"] is False
        assert result["alert"] is False