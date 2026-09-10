from datetime import datetime


VALID_LEVELS = {
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL"
}

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


def parse_log_line(line):
    """
    Parse a single log line safely.

    Returns:
        A structured log dictionary if valid.
        None if the line is invalid.
    """

    if not isinstance(line, str):
        return None

    line = line.strip()

    if not line:
        return None

    parts = line.split(" ", 3)

    if len(parts) != 4:
        return None

    timestamp = f"{parts[0]} {parts[1]}"
    level = parts[2].strip().upper()
    message = parts[3].strip()

    try:
        datetime.strptime(
            timestamp,
            TIMESTAMP_FORMAT
        )
    except ValueError:
        return None

    if level not in VALID_LEVELS:
        return None

    if not message:
        return None

    return {
        "timestamp": timestamp,
        "level": level,
        "message": message
    }


def parse_log_file(file_path="sample_logs/app.log"):
    """
    Safely parse a log file into structured log dictionaries.

    Invalid lines are skipped instead of crashing.
    """

    logs = []
    invalid_lines = []

    if not isinstance(file_path, str) or not file_path.strip():
        print("Error: Invalid log file path.")
        return logs

    file_path = file_path.strip()

    try:
        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            for line_number, line in enumerate(
                file,
                start=1
            ):

                parsed_log = parse_log_line(line)

                if parsed_log is None:

                    if line.strip():
                        invalid_lines.append(
                            line_number
                        )

                    continue

                logs.append(parsed_log)

    except FileNotFoundError:
        print(
            f"Error: Log file not found: {file_path}"
        )

    except PermissionError:
        print(
            f"Error: Permission denied: {file_path}"
        )

    except UnicodeDecodeError:
        print(
            f"Error: Unable to read log file encoding: "
            f"{file_path}"
        )

    except OSError as error:
        print(
            f"Error reading log file: {error}"
        )

    if invalid_lines:

        print(
            f"Warning: Skipped "
            f"{len(invalid_lines)} invalid log line(s)."
        )

    return logs