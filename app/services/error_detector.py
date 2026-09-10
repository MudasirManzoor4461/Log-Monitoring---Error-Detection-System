VALID_ERROR_LEVELS = {"WARNING", "ERROR", "CRITICAL"}


def detect_error(logs):
    """
    Detect WARNING, ERROR and CRITICAL logs safely.

    Invalid input or malformed log records are ignored
    instead of crashing the application.
    """

    if logs is None:
        return []

    if not isinstance(logs, list):
        return []

    detected_logs = []

    for log in logs:

        # Ignore invalid log records
        if not isinstance(log, dict):
            continue

        level = log.get("level")

        # Level must be a string
        if not isinstance(level, str):
            continue

        level = level.strip().upper()

        # Detect only valid error levels
        if level in VALID_ERROR_LEVELS:
            detected_logs.append(log)

    return detected_logs


def classify_error(log):
    """
    Classify an error safely based on its message.

    Returns UNKNOWN_ERROR for invalid or unexpected input.
    """

    # Validate log
    if not isinstance(log, dict):
        return "UNKNOWN_ERROR"

    message = log.get("message", "")

    # Message must be a string
    if not isinstance(message, str):
        return "UNKNOWN_ERROR"

    message = message.strip().lower()

    # Empty message
    if not message:
        return "UNKNOWN_ERROR"

    # Database errors
    if "database" in message:
        return "DATABASE_ERROR"

    # Authentication errors
    if "username" in message or "password" in message:
        return "AUTHENTICATION_ERROR"

    # Network errors
    if "network" in message or "timeout" in message:
        return "NETWORK_ERROR"

    # Payment errors
    if "payment" in message or "gateway" in message:
        return "PAYMENT_ERROR"

    # API errors
    if "api" in message:
        return "API_ERROR"

    return "UNKNOWN_ERROR"