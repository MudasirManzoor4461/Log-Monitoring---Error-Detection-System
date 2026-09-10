from collections import Counter
from datetime import datetime


ERROR_LEVELS = {"WARNING", "ERROR", "CRITICAL"}

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


def generate_analytics(logs):
    """
    Generate analytics from log records.

    The function safely handles:
    - None input
    - Empty input
    - Invalid log records
    - Missing fields
    - Unexpected data types
    """

    if logs is None:
        logs = []

    if not isinstance(logs, list):
        return {
            "success": False,
            "error": "Invalid logs input. Expected a list.",
            "total_logs": 0,
            "total_errors": 0,
            "total_warnings": 0,
            "total_critical": 0,
            "logs_by_level": {},
            "errors_by_category": {},
            "most_common_error": None,
            "error_rate": 0.0
        }

    total_logs = 0
    total_errors = 0
    total_warnings = 0
    total_critical = 0

    level_counts = Counter()
    category_counts = Counter()

    for log in logs:

        if not isinstance(log, dict):
            continue

        level = log.get("level")
        category = log.get("category")

        if not isinstance(level, str):
            continue

        level = level.strip().upper()

        if not level:
            continue

        total_logs += 1
        level_counts[level] += 1

        if level in ERROR_LEVELS:
            total_errors += 1

        if level == "WARNING":
            total_warnings += 1

        if level == "CRITICAL":
            total_critical += 1

        if isinstance(category, str):

            category = category.strip()

            if category:
                category_counts[category] += 1

    if total_logs > 0:
        error_rate = round(
            (total_errors / total_logs) * 100,
            2
        )
    else:
        error_rate = 0.0

    most_common_error = None

    if category_counts:
        most_common_error = category_counts.most_common(1)[0][0]

    return {
        "success": True,
        "total_logs": total_logs,
        "total_errors": total_errors,
        "total_warnings": total_warnings,
        "total_critical": total_critical,
        "logs_by_level": dict(level_counts),
        "errors_by_category": dict(category_counts),
        "most_common_error": most_common_error,
        "error_rate": error_rate
    }


def generate_error_trends(logs):
    """
    Generate hourly error trends from log records.

    Only WARNING, ERROR and CRITICAL logs are counted.

    Invalid records are ignored safely.
    """

    if logs is None:
        return []

    if not isinstance(logs, list):
        return []

    trends = Counter()

    for log in logs:

        if not isinstance(log, dict):
            continue

        level = log.get("level")
        timestamp = log.get("timestamp")

        if not isinstance(level, str):
            continue

        if not isinstance(timestamp, str):
            continue

        level = level.strip().upper()
        timestamp = timestamp.strip()

        if level not in ERROR_LEVELS:
            continue

        try:
            parsed_timestamp = datetime.strptime(
                timestamp,
                TIMESTAMP_FORMAT
            )
        except ValueError:
            continue

        hour = parsed_timestamp.strftime(
            "%Y-%m-%d %H:00:00"
        )

        trends[hour] += 1

    return [
        {
            "time": hour,
            "error_count": count
        }
        for hour, count in sorted(trends.items())
    ]