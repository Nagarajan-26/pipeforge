from enum import StrEnum


class TopologyType(StrEnum):
    LINEAR = "linear"
    BRANCHING = "branching"
    MULTI_SOURCE_CONVERGENCE = "multi_source_convergence"


class NodeType(StrEnum):
    SOURCE = "source"
    TRANSFORMATION = "transformation"
    DATASET = "dataset"
    CONSUMER = "consumer"


class FaultType(StrEnum):
    INGESTION_FAILURE = "ingestion_failure"
    SCHEMA_DRIFT = "schema_drift"
    TRANSFORMATION_FAILURE = "transformation_failure"
    DATA_QUALITY_ANOMALY = "data_quality_anomaly"


class EventStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"
    RUNNING = "running"


class SignalMetric(StrEnum):
    ROW_COUNT = "row_count"
    FRESHNESS_MINUTES = "freshness_minutes"
    NULL_RATE = "null_rate"
    DUPLICATE_RATE = "duplicate_rate"
    INVALID_RECORD_COUNT = "invalid_record_count"
    SCHEMA_VERSION = "schema_version"


class Severity(StrEnum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ImpactType(StrEnum):
    STALE_DATA = "stale_data"
    INCOMPLETE_DATA = "incomplete_data"
    UNAVAILABLE_REPORT = "unavailable_report"
    INCORRECT_METRIC = "incorrect_metric"
