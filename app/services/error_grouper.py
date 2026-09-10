from collections import defaultdict
from datetime import datetime


TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


def group_errors(logs):
    """
    Group error logs by category safely.

    Invalid records are ignored instead of crashing the application.
    """

    if logs is None:
        return {}

    if not isinstance(logs, list):
        return {}

    grouped_errors = defaultdict(list)

    for log in logs:

        # Log must be a dictionary
        if not isinstance(log, dict):
            continue

        category = log.get("category")
        timestamp = log.get("timestamp")

        # Validate category
        if not isinstance(category, str):
            category = "UNKNOWN_ERROR"
        else:
            category = category.strip()

            if not category:
                category = "UNKNOWN_ERROR"

        # Validate timestamp
        if not isinstance(timestamp, str):
            continue

        timestamp = timestamp.strip()

        try:
            datetime.strptime(
                timestamp,
                TIMESTAMP_FORMAT
            )
        except ValueError:
            continue

        grouped_errors[category].append(log)

    error_summary = {}

    for category, category_logs in grouped_errors.items():

        timestamps = []

        for log in category_logs:

            try:
                timestamp = datetime.strptime(
                    log["timestamp"],
                    TIMESTAMP_FORMAT
                )

                timestamps.append(timestamp)

            except (ValueError, TypeError, KeyError):
                continue

        # Skip category if no valid timestamps remain
        if not timestamps:
            continue

        error_summary[category] = {
            "category": category,
            "count": len(category_logs),
            "first_seen": min(timestamps).strftime(
                TIMESTAMP_FORMAT
            ),
            "last_seen": max(timestamps).strftime(
                TIMESTAMP_FORMAT
            )
        }

    return error_summary