import threading
from typing import Any

from app.services.live_monitor import process_new_log_line
from app.services.log_monitor import LogMonitor

from app.database.connection import get_connection
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from app.database.repositories import (
    delete_log_by_id,
    get_all_logs,
    get_logs_by_category,
    get_logs_by_level,
    get_logs_by_time_range,
    save_logs,
    search_logs_by_message,
)
from app.schemas.log_schema import (
    AcknowledgeAlertResponse,
    AlertListResponse,
    AnalyticsResponse,
    DeleteLogResponse,
    ErrorLogsResponse,
    ErrorResponse,
    ErrorTrendResponse,
    ErrorTrendsResponse,
    IngestLogsResponse,
    LogListResponse,
    SearchLogsResponse,
    TimeRangeLogsResponse,
    TopErrorsResponse,
)

from app.database.repositories import (
    acknowledge_alert,
    get_all_alerts,
    get_unacknowledged_alerts,
)

from app.services.analytics import generate_analytics, generate_error_trends
from app.services.error_detector import classify_error, detect_error
from app.services.error_grouper import group_errors
from app.services.log_parser import (
    parse_log_file,
    parse_log_line
)

router = APIRouter()

VALID_LEVELS = {
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL"
}

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


def convert_logs_to_dict(logs):
    """
    Convert SQLite Row objects into normal dictionaries.
    """

    converted_logs = []

    for log in logs:

        if hasattr(log, "keys"):

            converted_logs.append({
                "id": log["id"],
                "timestamp": log["timestamp"],
                "level": log["level"],
                "message": log["message"],
                "category": log["category"]
            })

    return converted_logs

@router.get("/health")
def health_check():
    """
    Health check endpoint.

    Verifies both:
    - Application availability
    - Database connectivity
    """

    connection = None

    try:
        connection = get_connection()

        connection.execute(
            "SELECT 1"
        )

        return {
            "status": "healthy",
            "service": "log-monitoring-system",
            "database": "healthy"
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "service": "log-monitoring-system",
                "database": "unavailable"
            }
        )

    finally:
        if connection:
            connection.close()

@router.get(
    "/logs",
    response_model=LogListResponse,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid log level or category."
        }
    }
)
def get_logs(
    level: str | None = Query(
        default=None,
        description="Filter logs by level"
    ),
    category: str | None = Query(
        default=None,
        description="Filter logs by error category"
    ),
    page: int = Query(
        default=1,
        ge=1,
        description="Page number"
    ),
    page_size: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of logs per page"
    )
):
    """
    Get logs with optional level/category filters and pagination.
    """

    if level is not None:

        level = level.strip().upper()

        if level not in VALID_LEVELS:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid log level. "
                    "Use INFO, WARNING, ERROR or CRITICAL."
                )
            )

    if category is not None:

        category = category.strip()

        if not category:

            raise HTTPException(
                status_code=400,
                detail="Category cannot be empty."
            )

    if level is not None and category is not None:

        logs = get_logs_by_level(level)

        logs = [
            log
            for log in logs
            if log["category"] == category
        ]

    elif level is not None:

        logs = get_logs_by_level(level)

    elif category is not None:

        logs = get_logs_by_category(category)

    else:

        logs = get_all_logs()

    total_logs = len(logs)

    total_pages = (
        (total_logs + page_size - 1) // page_size
        if total_logs > 0
        else 0
    )

    start = (page - 1) * page_size
    end = start + page_size

    paginated_logs = logs[start:end]

    converted_logs = convert_logs_to_dict(
        paginated_logs
    )

    return {
        "success": True,
        "count": len(converted_logs),
        "total_logs": total_logs,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "logs": converted_logs
    }


@router.get(
    "/logs/errors",
    response_model=ErrorLogsResponse
)
def get_error_logs():
    """
    Return all WARNING, ERROR and CRITICAL logs.
    """

    logs = get_all_logs()

    converted_logs = convert_logs_to_dict(logs)

    errors = detect_error(converted_logs)

    return {
        "success": True,
        "count": len(errors),
        "errors": errors
    }


@router.get(
    "/errors",
    response_model=ErrorLogsResponse
)
def get_errors():
    """
    Return all detected errors.
    """

    logs = get_all_logs()

    converted_logs = convert_logs_to_dict(logs)

    errors = detect_error(converted_logs)

    return {
        "success": True,
        "count": len(errors),
        "errors": errors
    }


@router.get(
    "/errors/top",
    response_model=TopErrorsResponse
)
def get_top_errors():
    """
    Return error categories sorted by frequency.
    """

    logs = get_all_logs()

    converted_logs = convert_logs_to_dict(logs)

    errors = detect_error(converted_logs)

    categorized_errors = []

    for error in errors:

        category = classify_error(error)

        error["category"] = category

        categorized_errors.append(error)

    grouped = group_errors(
        categorized_errors
    )

    sorted_errors = sorted(
        grouped.values(),
        key=lambda item: item["count"],
        reverse=True
    )

    return {
        "success": True,
        "count": len(sorted_errors),
        "errors": sorted_errors
    }


@router.get(
        "/analytics",
        response_model=AnalyticsResponse)
def analytics():
    """
    Generate analytics from stored logs.
    """

    logs = get_all_logs()

    converted_logs = convert_logs_to_dict(logs)

    for log in converted_logs:

        if log["level"] in {
            "WARNING",
            "ERROR",
            "CRITICAL"
        }:

            log["category"] = classify_error(log)

    return generate_analytics(
        converted_logs
    )



@router.get("/analytics/trends", response_model=ErrorTrendsResponse)
def error_trends():
    """
    Return hourly error trends.
    """

    logs = get_all_logs()

    converted_logs = convert_logs_to_dict(logs)

    trends = generate_error_trends(
        converted_logs
    )

    return {
        "success": True,
        "count": len(trends),
        "trends": trends
    }



@router.get(
    "/logs/search",
    response_model=SearchLogsResponse,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid search query."
        }
    }
)
def search_logs(
    q: str = Query(
    ...,
    min_length=1,
    max_length=200,
    description="Search term for log messages"
    ),
    page: int = Query(
        default=1,
        ge=1
    ),
    page_size: int = Query(
        default=10,
        ge=1,
        le=100
    )
):
    """
    Search logs by message content.
    """

    q = q.strip()

    if not q:

        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty."
        )

    result = search_logs_by_message(
        q,
        page,
        page_size
    )

    if not result["success"]:

        raise HTTPException(
            status_code=400,
            detail=result.get(
                "message",
                "Invalid search request."
            )
        )

    result["logs"] = convert_logs_to_dict(
        result["logs"]
    )

    return result


@router.get(
    "/logs/time-range",
    response_model=TimeRangeLogsResponse,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid timestamp range."
        }
    }
)
def logs_by_time_range(
    start_time: str = Query(
        ...,
        description="Start timestamp: YYYY-MM-DD HH:MM:SS"
    ),
    end_time: str = Query(
        ...,
        description="End timestamp: YYYY-MM-DD HH:MM:SS"
    )
):
    """
    Return logs between two timestamps.
    """

    start_time = start_time.strip()
    end_time = end_time.strip()

    try:

        start_datetime = datetime.strptime(
            start_time,
            TIMESTAMP_FORMAT
        )

        end_datetime = datetime.strptime(
            end_time,
            TIMESTAMP_FORMAT
        )

    except ValueError:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid timestamp format. "
                "Use YYYY-MM-DD HH:MM:SS."
            )
        )

    if start_datetime > end_datetime:

        raise HTTPException(
            status_code=400,
            detail=(
                "start_time cannot be greater than end_time."
            )
        )

    logs = get_logs_by_time_range(
        start_time,
        end_time
    )

    converted_logs = convert_logs_to_dict(logs)

    return {
        "success": True,
        "count": len(converted_logs),
        "start_time": start_time,
        "end_time": end_time,
        "logs": converted_logs
    }


@router.delete(
    "/logs/{log_id}",
    response_model=DeleteLogResponse,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid log ID."
        },
        404: {
            "model": ErrorResponse,
            "description": "Log not found."
        },
        500: {
            "model": ErrorResponse,
            "description": "Internal server error."
        }
    }
)
def delete_log(log_id: int):
    """
    Delete a single log by ID.

    HTTP status codes:
    - 200: Successfully deleted
    - 400: Invalid ID
    - 404: Log not found
    - 500: Database/unexpected error
    """

    result = delete_log_by_id(log_id)

    if not isinstance(result, dict):

        raise HTTPException(
            status_code=500,
            detail="Unexpected response from database layer."
        )

    if result.get("success") is True:

        return result

    message = result.get(
        "message",
        "Unable to delete log."
    )

    if message.startswith("Invalid log ID"):

        raise HTTPException(
            status_code=400,
            detail=message
        )

    if message == "Log not found.":

        raise HTTPException(
            status_code=404,
            detail=message
        )

    if message == "Database error while deleting log.":

        raise HTTPException(
            status_code=500,
            detail="Internal server error while deleting log."
        )

    raise HTTPException(
        status_code=500,
        detail="Unable to delete log."
    )


@router.post(
    "/logs/ingest",
    response_model=IngestLogsResponse,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid file path."
        },
        404: {
            "model": ErrorResponse,
            "description": "Log file not found."
        },
        500: {
            "model": ErrorResponse,
            "description": "Database error while saving logs."
        }
    }
)
def ingest_logs(
    file_path: str = Query(
        default="sample_logs/app.log",
        description="Path of the log file inside sample_logs directory"
    )
):
    """
    Parse a log file, detect errors, classify them,
    and save valid logs into the database.

    For security reasons, only files inside the
    sample_logs directory are allowed.
    """

    if not isinstance(file_path, str):
        raise HTTPException(
            status_code=400,
            detail="Invalid file path."
        )

    file_path = file_path.strip()

    if not file_path:
        raise HTTPException(
            status_code=400,
            detail="File path cannot be empty."
        )

    # --------------------------------------------------------
    # Security: restrict file access to sample_logs directory
    # --------------------------------------------------------

    allowed_directory = Path("sample_logs").resolve()

    requested_path = Path(file_path)

    if requested_path.is_absolute():
        raise HTTPException(
            status_code=400,
            detail="Absolute file paths are not allowed."
        )

    try:
        safe_path = requested_path.resolve()

        safe_path.relative_to(allowed_directory)

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="File path must be inside the sample_logs directory."
        )

    # --------------------------------------------------------
    # Validate file
    # --------------------------------------------------------

    if not safe_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Log file not found."
        )

    if not safe_path.is_file():
        raise HTTPException(
            status_code=400,
            detail="Provided path is not a file."
        )

    # --------------------------------------------------------
    # Parse logs
    # --------------------------------------------------------

    logs = parse_log_file(str(safe_path))

    if not logs:
        return {
            "success": True,
            "parsed_logs": 0,
            "detected_errors": 0,
            "saved": {
                "success": True,
                "inserted_logs": 0,
                "duplicate_logs": 0,
                "skipped_logs": 0
            }
        }

    # --------------------------------------------------------
    # Detect and classify errors
    # --------------------------------------------------------

    errors = detect_error(logs)

    for error in errors:
        error["category"] = classify_error(error)

    # --------------------------------------------------------
    # Save logs
    # --------------------------------------------------------

    save_result = save_logs(logs)

    if not isinstance(save_result, dict):
        raise HTTPException(
            status_code=500,
            detail="Unexpected response from database layer."
        )

    if not save_result.get("success"):
        raise HTTPException(
            status_code=500,
            detail="Unable to save logs to database."
        )

    return {
        "success": True,
        "parsed_logs": len(logs),
        "detected_errors": len(errors),
        "saved": save_result
    }


@router.get(
    "/alerts",
    response_model=AlertListResponse
)
def get_alerts():
    """
    Return all alerts.
    """

    alerts = get_all_alerts()

    converted_alerts = []

    for alert in alerts:

        converted_alerts.append({
            "id": alert["id"],
            "log_id": alert["log_id"],
            "level": alert["level"],
            "category": alert["category"],
            "message": alert["message"],
            "created_at": alert["created_at"],
            "acknowledged": bool(alert["acknowledged"])
        })

    return {
        "success": True,
        "count": len(converted_alerts),
        "alerts": converted_alerts
    }


@router.get("/alerts/unacknowledged",response_model=AlertListResponse)
def get_unacknowledged():
    """
    Return all unacknowledged alerts.
    """

    alerts = get_unacknowledged_alerts()

    converted_alerts = []

    for alert in alerts:

        converted_alerts.append({
            "id": alert["id"],
            "log_id": alert["log_id"],
            "level": alert["level"],
            "category": alert["category"],
            "message": alert["message"],
            "created_at": alert["created_at"],
            "acknowledged": bool(alert["acknowledged"])
        })

    return {
        "success": True,
        "count": len(converted_alerts),
        "alerts": converted_alerts
    }

@router.patch(
    "/alerts/{alert_id}/acknowledge",
    response_model=AcknowledgeAlertResponse,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid alert ID."
        },
        404: {
            "model": ErrorResponse,
            "description": "Alert not found."
        }
    }
)
def acknowledge_alert_route(alert_id: int):
    """
    Acknowledge a specific alert.
    """

    result = acknowledge_alert(alert_id)

    if not isinstance(result, dict):

        raise HTTPException(
            status_code=500,
            detail="Unexpected response from database layer."
        )

    if not result.get("success"):

        message = result.get(
            "message",
            "Unable to acknowledge alert."
        )

        if message == "Alert not found.":

            raise HTTPException(
                status_code=404,
                detail=message
            )

        raise HTTPException(
            status_code=400,
            detail=message
        )

    return {
        "success": True,
        "acknowledged": bool(
            result.get("updated", False)
        ),
        "message": result.get(
            "message",
            "Alert acknowledged successfully."
        )
    }


@router.post("/logs/upload")
async def upload_log_file(
    file: UploadFile = File(...)
):
    """
    Upload, analyze and calculate analytics
    for the uploaded log file only.

    The uploaded file is processed in memory.
    No user-supplied file path is used.
    """

    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

    ALLOWED_EXTENSIONS = {
        ".log",
        ".txt"
    }

    # -----------------------------------------
    # Validate file
    # -----------------------------------------

    if file is None:
        raise HTTPException(
            status_code=400,
            detail="No file was uploaded."
        )

    filename = file.filename or ""

    if not filename.strip():
        raise HTTPException(
            status_code=400,
            detail="Uploaded file must have a filename."
        )

    safe_filename = Path(filename).name

    if safe_filename != filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename."
        )

    extension = Path(safe_filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only .log and .txt files are allowed."
        )

    # -----------------------------------------
    # Read file safely
    # -----------------------------------------

    try:

        file_content = await file.read(
            MAX_FILE_SIZE + 1
        )

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Unable to read uploaded file."
        )

    finally:

        await file.close()

    # -----------------------------------------
    # Validate file content
    # -----------------------------------------

    if not file_content:

        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    if len(file_content) > MAX_FILE_SIZE:

        raise HTTPException(
            status_code=400,
            detail="File size cannot exceed 5 MB."
        )

    try:

        content = file_content.decode("utf-8")

    except UnicodeDecodeError:

        raise HTTPException(
            status_code=400,
            detail="Uploaded file must use UTF-8 encoding."
        )

    # -----------------------------------------
    # Parse logs
    # -----------------------------------------

    parsed_logs = []

    invalid_lines = 0

    for line in content.splitlines():

        if not line.strip():
            continue

        parsed_log = parse_log_line(line)

        if parsed_log is None:

            invalid_lines += 1

            continue

        parsed_logs.append(parsed_log)

    # -----------------------------------------
    # No valid logs
    # -----------------------------------------

    if not parsed_logs:

        return {
            "success": True,
            "filename": safe_filename,
            "parsed_logs": 0,
            "detected_errors": 0,
            "invalid_lines": invalid_lines,
            "analytics": {
                "total_logs": 0,
                "total_errors": 0,
                "total_warnings": 0,
                "total_critical": 0,
                "logs_by_level": {},
                "errors_by_category": {},
                "most_common_error": None,
                "error_rate": 0.0
            },
            "errors": [],
            "saved": {
                "success": True,
                "inserted_logs": 0,
                "duplicate_logs": 0,
                "skipped_logs": 0
            }
        }

    # -----------------------------------------
    # Detect errors
    # -----------------------------------------

    errors = detect_error(parsed_logs)

    # -----------------------------------------
    # Classify errors
    # -----------------------------------------

    for log in parsed_logs:

        if log["level"] in {
            "WARNING",
            "ERROR",
            "CRITICAL"
        }:

            log["category"] = classify_error(log)

        else:

            log["category"] = None

    # -----------------------------------------
    # Calculate analytics for uploaded file
    # -----------------------------------------

    total_logs = len(parsed_logs)

    total_errors = 0

    total_warnings = 0

    total_critical = 0

    logs_by_level = {}

    errors_by_category = {}


    for log in parsed_logs:

        level = log["level"]

        logs_by_level[level] = (
            logs_by_level.get(level, 0) + 1
        )


        if level in {
            "WARNING",
            "ERROR",
            "CRITICAL"
        }:

            total_errors += 1


        if level == "WARNING":

            total_warnings += 1


        if level == "CRITICAL":

            total_critical += 1


        category = log.get("category")

        if category:

            errors_by_category[category] = (
                errors_by_category.get(category, 0) + 1
            )


    # -----------------------------------------
    # Error rate
    # -----------------------------------------

    if total_logs > 0:

        error_rate = round(
            (total_errors / total_logs) * 100,
            2
        )

    else:

        error_rate = 0.0


    # -----------------------------------------
    # Most common error
    # -----------------------------------------

    most_common_error = None

    if errors_by_category:

        most_common_error = max(
            errors_by_category,
            key=errors_by_category.get
        )


    # -----------------------------------------
    # Save logs
    # -----------------------------------------

    save_result = save_logs(
        parsed_logs
    )


    if not isinstance(
        save_result,
        dict
    ):

        raise HTTPException(
            status_code=500,
            detail="Unexpected response from database layer."
        )


    if not save_result.get("success"):

        raise HTTPException(
            status_code=500,
            detail="Unable to save uploaded logs."
        )


    # -----------------------------------------
    # Return complete result
    # -----------------------------------------

    return {

        "success": True,

        "filename": safe_filename,

        "parsed_logs": total_logs,

        "detected_errors": total_errors,

        "invalid_lines": invalid_lines,

        "analytics": {

            "total_logs": total_logs,

            "total_errors": total_errors,

            "total_warnings": total_warnings,

            "total_critical": total_critical,

            "logs_by_level": logs_by_level,

            "errors_by_category": errors_by_category,

            "most_common_error": most_common_error,

            "error_rate": error_rate

        },

        "errors": errors,

        "saved": save_result

    }

# ============================================================
# LIVE LOG MONITORING
# ============================================================

# Global live-monitoring state.
#
# Only one live monitor is allowed at a time.
# This prevents multiple threads from monitoring
# the same file accidentally.
live_monitor_state = {
    "running": False,
    "file_path": None,
    "interval": None,
    "error": None
}

live_monitor_instance = None
live_monitor_thread = None

live_monitor_lock = threading.Lock()


def _run_live_monitor(
    monitor: LogMonitor
):
    """
    Background worker for live log monitoring.

    The worker continuously reads newly added lines
    and sends each line through process_new_log_line().
    """

    global live_monitor_instance

    try:

        for line in monitor.start():

            result = process_new_log_line(
                line
            )

            # Keep the worker alive even if one
            # individual log line cannot be processed.
            if not isinstance(result, dict):

                continue

            if not result.get("success"):

                print(
                    "Live monitor skipped line:",
                    result.get(
                        "message",
                        "Unknown processing error."
                    )
                )

    except Exception as error:

        with live_monitor_lock:

            live_monitor_state["running"] = False

            live_monitor_state["error"] = str(
                error
            )

        print(
            f"Live monitoring stopped because of an error: {error}"
        )

    finally:

        with live_monitor_lock:

            live_monitor_state["running"] = False

            live_monitor_instance = None


@router.post(
    "/live-monitor/start"
)
def start_live_monitor_api(
    file_path: str = Query(
        default="sample_logs/app.log",
        description=(
            "Log file path inside sample_logs directory."
        )
    ),
    interval: float = Query(
        default=1.0,
        gt=0,
        le=60,
        description=(
            "Polling interval in seconds."
        )
    )
):
    """
    Start background live log monitoring.

    Security:
    Only files inside sample_logs are allowed.

    Only one monitor can run at a time.
    """

    global live_monitor_instance
    global live_monitor_thread

    # --------------------------------------------------------
    # Validate file path
    # --------------------------------------------------------

    if not isinstance(
        file_path,
        str
    ):

        raise HTTPException(
            status_code=400,
            detail="Invalid file path."
        )

    file_path = file_path.strip()

    if not file_path:

        raise HTTPException(
            status_code=400,
            detail="File path cannot be empty."
        )

    # --------------------------------------------------------
    # Security: restrict monitoring to sample_logs
    # --------------------------------------------------------

    allowed_directory = Path(
        "sample_logs"
    ).resolve()

    requested_path = Path(
        file_path
    )

    if requested_path.is_absolute():

        raise HTTPException(
            status_code=400,
            detail="Absolute file paths are not allowed."
        )

    try:

        safe_path = requested_path.resolve()

        safe_path.relative_to(
            allowed_directory
        )

    except ValueError:

        raise HTTPException(
            status_code=400,
            detail=(
                "File path must be inside "
                "the sample_logs directory."
            )
        )

    # --------------------------------------------------------
    # Validate file
    # --------------------------------------------------------

    if not safe_path.exists():

        raise HTTPException(
            status_code=404,
            detail="Log file not found."
        )

    if not safe_path.is_file():

        raise HTTPException(
            status_code=400,
            detail="Provided path is not a file."
        )

    # --------------------------------------------------------
    # Validate interval
    # --------------------------------------------------------

    if isinstance(
        interval,
        bool
    ):

        raise HTTPException(
            status_code=400,
            detail="Monitoring interval must be a number."
        )

    if interval <= 0:

        raise HTTPException(
            status_code=400,
            detail=(
                "Monitoring interval must be "
                "greater than 0."
            )
        )

    # --------------------------------------------------------
    # Prevent multiple monitors
    # --------------------------------------------------------

    with live_monitor_lock:

        if live_monitor_state["running"]:

            return {
                "success": False,
                "running": True,
                "message": (
                    "Live monitoring is already running."
                ),
                "file_path": live_monitor_state[
                    "file_path"
                ],
                "interval": live_monitor_state[
                    "interval"
                ]
            }

        # ----------------------------------------------------
        # Create monitor
        # ----------------------------------------------------

        try:

            monitor = LogMonitor(
                file_path=str(
                    safe_path
                ),
                interval=interval
            )

        except Exception as error:

            raise HTTPException(
                status_code=400,
                detail=str(error)
            )

        live_monitor_instance = monitor

        live_monitor_state["running"] = True

        live_monitor_state["file_path"] = str(
            safe_path
        )

        live_monitor_state["interval"] = interval

        live_monitor_state["error"] = None

        # ----------------------------------------------------
        # Start background thread
        # ----------------------------------------------------

        live_monitor_thread = threading.Thread(
            target=_run_live_monitor,
            args=(monitor,),
            daemon=True,
            name="log-monitor-thread"
        )

        live_monitor_thread.start()

    return {
        "success": True,
        "running": True,
        "message": (
            "Live monitoring started successfully."
        ),
        "file_path": str(
            safe_path
        ),
        "interval": interval
    }


@router.post(
    "/live-monitor/stop"
)
def stop_live_monitor_api():
    """
    Stop the currently running live monitor.
    """

    global live_monitor_instance

    with live_monitor_lock:

        if not live_monitor_state["running"]:

            return {
                "success": True,
                "running": False,
                "message": (
                    "Live monitoring is not running."
                )
            }

        monitor = live_monitor_instance

        if monitor is not None:

            try:

                monitor.stop()

            except Exception as error:

                live_monitor_state["error"] = str(
                    error
                )

                raise HTTPException(
                    status_code=500,
                    detail=(
                        "Unable to stop live monitoring."
                    )
                )

        live_monitor_state["running"] = False

        live_monitor_instance = None

    return {
        "success": True,
        "running": False,
        "message": (
            "Live monitoring stopped successfully."
        )
    }


@router.get(
    "/live-monitor/status"
)
def live_monitor_status():
    """
    Return the current live-monitoring status.
    """

    with live_monitor_lock:

        return {
            "success": True,
            "running": bool(
                live_monitor_state["running"]
            ),
            "file_path": (
                live_monitor_state["file_path"]
                if live_monitor_state["running"]
                else None
            ),
            "interval": (
                live_monitor_state["interval"]
                if live_monitor_state["running"]
                else None
            ),
            "error": live_monitor_state["error"]
        }

