ALERT_LEVELS = {
    "ERROR",
    "CRITICAL"
}


def generate_alert(log):
    """
    Generate an alert for ERROR and CRITICAL logs.

    WARNING and INFO logs do not generate alerts.

    Invalid input is handled safely.
    """

    if not isinstance(log, dict):
        return {
            "success": False,
            "alert": False,
            "message": "Invalid log record."
        }

    level = log.get("level")

    if not isinstance(level, str):
        return {
            "success": False,
            "alert": False,
            "message": "Invalid log level."
        }

    level = level.strip().upper()

    if not level:
        return {
            "success": False,
            "alert": False,
            "message": "Log level cannot be empty."
        }

    if level not in {
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL"
    }:
        return {
            "success": False,
            "alert": False,
            "message": "Unknown log level."
        }

    if level not in ALERT_LEVELS:
        return {
            "success": True,
            "alert": False,
            "message": "No alert required."
        }

    message = log.get("message")

    if not isinstance(message, str):
        message = "No error message provided."

    message = message.strip()

    if level == "CRITICAL":
        alert_message = (
            f"CRITICAL ALERT: {message}"
        )

    else:
        alert_message = (
            f"ERROR ALERT: {message}"
        )

    return {
        "success": True,
        "alert": True,
        "level": level,
        "message": alert_message
    }