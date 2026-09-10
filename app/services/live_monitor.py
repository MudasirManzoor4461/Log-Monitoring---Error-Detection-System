from app.database.repositories import (
    save_alert,
    save_log_and_get_id
)

from app.services.alert_service import generate_alert
from app.services.error_detector import classify_error, detect_error
from app.services.log_monitor import LogMonitor
from app.services.log_parser import parse_log_line


def process_new_log_line(line):
    """
    Process a newly detected log line safely.

    Flow:
        New line
        -> parse
        -> detect error
        -> classify error
        -> save log and get log ID
        -> generate alert
        -> save alert with log ID
    """

    if not isinstance(line, str):
        return {
            "success": False,
            "message": "Invalid log line."
        }

    line = line.strip()

    if not line:
        return {
            "success": False,
            "message": "Log line cannot be empty."
        }

    # -----------------------------
    # Parse log
    # -----------------------------

    parsed_log = parse_log_line(line)

    if parsed_log is None:
        return {
            "success": False,
            "message": "Invalid log format."
        }

    logs = [parsed_log]

    # -----------------------------
    # Detect errors
    # -----------------------------

    errors = detect_error(logs)

    # -----------------------------
    # Classify errors
    # -----------------------------

    for error in errors:
        error["category"] = classify_error(error)

    if errors:
        parsed_log["category"] = errors[0]["category"]

    # -----------------------------
    # Save log and get database ID
    # -----------------------------

    save_result = save_log_and_get_id(parsed_log)

    if not isinstance(save_result, dict):
        return {
            "success": False,
            "message": "Unexpected database response."
        }

    if not save_result.get("success"):
        return {
            "success": False,
            "message": save_result.get(
                "message",
                "Unable to save log."
            )
        }

    log_id = save_result.get("log_id")

    if not isinstance(log_id, int) or log_id <= 0:
        return {
            "success": False,
            "message": "Invalid log ID returned by database."
        }

    # -----------------------------
    # Generate alert
    # -----------------------------

    alert_result = generate_alert(parsed_log)

    if not isinstance(alert_result, dict):
        return {
            "success": False,
            "message": "Unexpected alert response."
        }

    # -----------------------------
    # Save alert to database
    # -----------------------------

    saved_alert = None

    if (
        alert_result.get("success")
        and alert_result.get("alert") is True
    ):

        saved_alert = save_alert(
            {
                "log_id": log_id,
                "level": parsed_log["level"],
                "category": parsed_log.get("category"),
                "message": parsed_log["message"],
                "created_at": parsed_log["timestamp"]
            }
        )

        if not isinstance(saved_alert, dict):
            return {
                "success": False,
                "message": "Unexpected alert database response."
            }

        if not saved_alert.get("success"):
            return {
                "success": False,
                "message": saved_alert.get(
                    "message",
                    "Unable to save alert."
                )
            }

    # -----------------------------
    # Final result
    # -----------------------------

    return {
        "success": True,
        "log": parsed_log,
        "log_id": log_id,
        "is_error": len(errors) > 0,
        "category": (
            errors[0]["category"]
            if errors
            else None
        ),
        "saved": save_result,
        "alert": alert_result,
        "saved_alert": saved_alert
    }


def start_live_monitor(
    file_path="sample_logs/app.log",
    interval=1
):
    """
    Continuously monitor a log file and process
    newly added log lines.
    """

    monitor = LogMonitor(
        file_path=file_path,
        interval=interval
    )

    try:

        for line in monitor.start():

            result = process_new_log_line(line)

            if result["success"]:

                print(
                    "New log processed successfully:"
                )

                print(
                    result["log"]
                )

                print(
                    f"Log ID: {result['log_id']}"
                )

                if result["is_error"]:

                    print(
                        f"Error detected: "
                        f"{result['category']}"
                    )

                else:

                    print(
                        "No error detected."
                    )

                alert = result.get("alert")

                if (
                    isinstance(alert, dict)
                    and alert.get("alert") is True
                ):

                    print(
                        f"🚨 {alert['message']}"
                    )

                saved_alert = result.get(
                    "saved_alert"
                )

                if (
                    isinstance(saved_alert, dict)
                    and saved_alert.get("success")
                ):

                    print(
                        "Alert saved to database."
                    )

            else:

                print(
                    f"Skipped log: "
                    f"{result['message']}"
                )

    except KeyboardInterrupt:

        monitor.stop()

        print(
            "Live monitoring stopped."
        )

    except (
        FileNotFoundError,
        ValueError,
        OSError
    ) as error:

        monitor.stop()

        print(
            f"Live monitoring error: {error}"
        )