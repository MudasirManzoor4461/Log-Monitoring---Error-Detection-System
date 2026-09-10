from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LogResponse(BaseModel):
    """
    Response schema for a single log record.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(gt=0)
    timestamp: datetime
    level: str
    message: str
    category: str | None = None


class LogListResponse(BaseModel):
    """
    Paginated response schema for logs.
    """

    success: bool
    count: int = Field(ge=0)
    total_logs: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total_pages: int = Field(ge=0)
    logs: list[LogResponse]


class DeleteLogResponse(BaseModel):
    """
    Response schema for deleting a log.
    """

    success: bool
    deleted: bool
    message: str


class ErrorResponse(BaseModel):
    """
    Standard response schema for API errors.
    """

    detail: str


class SearchLogsResponse(BaseModel):
    """
    Paginated response schema for log search.
    """

    success: bool
    logs: list[LogResponse]
    total_logs: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total_pages: int = Field(ge=0)
    has_next: bool
    has_previous: bool


class TimeRangeLogsResponse(BaseModel):
    """
    Response schema for logs within a time range.
    """

    success: bool
    count: int = Field(ge=0)
    start_time: datetime
    end_time: datetime
    logs: list[LogResponse]


class ErrorLogsResponse(BaseModel):
    """
    Response schema for detected error logs.
    """

    success: bool
    count: int = Field(ge=0)
    errors: list[LogResponse]


class TopErrorResponse(BaseModel):
    """
    Response schema for a grouped error category.
    """

    category: str
    count: int = Field(ge=1)
    first_seen: datetime
    last_seen: datetime


class TopErrorsResponse(BaseModel):
    """
    Response schema for top error categories.
    """

    success: bool
    count: int = Field(ge=0)
    errors: list[TopErrorResponse]


class AnalyticsResponse(BaseModel):
    """
    Response schema for log analytics.
    """

    success: bool
    total_logs: int = Field(ge=0)
    total_errors: int = Field(ge=0)
    total_warnings: int = Field(ge=0)
    total_critical: int = Field(ge=0)
    logs_by_level: dict[str, int]
    errors_by_category: dict[str, int]
    most_common_error: str | None = None
    error_rate: float = Field(ge=0, le=100)


class SaveLogsResponse(BaseModel):
    """
    Response schema for database save operation.
    """

    success: bool
    inserted_logs: int = Field(ge=0)
    duplicate_logs: int = Field(ge=0)
    skipped_logs: int = Field(ge=0)


class IngestLogsResponse(BaseModel):
    """
    Response schema for log ingestion.
    """

    success: bool
    parsed_logs: int = Field(ge=0)
    detected_errors: int = Field(ge=0)
    saved: SaveLogsResponse


class ErrorTrendResponse(BaseModel):
    """
    Response schema for a single error trend.
    """

    time: datetime
    error_count: int = Field(ge=0)


class ErrorTrendsResponse(BaseModel):
    """
    Response schema for hourly error trends.
    """

    success: bool
    count: int = Field(ge=0)
    trends: list[ErrorTrendResponse]


class AlertResponse(BaseModel):
    """
    Response schema for a single alert.
    """

    id: int = Field(gt=0)
    log_id: int | None = Field(default=None, gt=0)
    level: str
    category: str | None = None
    message: str
    created_at: datetime
    acknowledged: bool


class AlertListResponse(BaseModel):
    """
    Response schema for a list of alerts.
    """

    success: bool
    count: int = Field(ge=0)
    alerts: list[AlertResponse]


class AcknowledgeAlertResponse(BaseModel):
    """
    Response schema for acknowledging an alert.
    """

    success: bool
    acknowledged: bool
    message: str