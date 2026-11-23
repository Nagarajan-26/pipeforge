from datetime import datetime
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    StringConstraints,
    field_validator,
)

from pipeforge.models.enums import (
    EventStatus,
    FaultType,
    ImpactType,
    NodeType,
    Severity,
    SignalMetric,
)

NonEmpty = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1),
]


class DomainModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        use_enum_values=False,
    )


class PipelineNode(DomainModel):
    node_id: NonEmpty
    name: NonEmpty
    node_type: NodeType
    system: NonEmpty
    criticality: Severity = Severity.MEDIUM


class PipelineEdge(DomainModel):
    source_node_id: NonEmpty
    target_node_id: NonEmpty
    relationship: NonEmpty = "depends_on"


class FaultInjection(DomainModel):
    fault_id: NonEmpty
    fault_type: FaultType
    target_node_id: NonEmpty
    injected_at: datetime
    description: NonEmpty

    @field_validator("injected_at")
    @classmethod
    def timestamp_must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("injected_at must include a timezone")
        return value


class ExecutionEvent(DomainModel):
    event_id: NonEmpty
    node_id: NonEmpty
    status: EventStatus
    started_at: datetime
    ended_at: datetime | None = None
    message: str = ""

    @field_validator("started_at", "ended_at")
    @classmethod
    def timestamps_must_be_timezone_aware(cls, value: datetime | None) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("Execution timestamps must include a timezone")
        return value

    @field_validator("ended_at")
    @classmethod
    def end_must_not_precede_start(cls, value: datetime | None, info) -> datetime | None:
        started_at = info.data.get("started_at")
        if value is not None and started_at is not None and value < started_at:
            raise ValueError("ended_at cannot precede started_at")
        return value


class DataQualitySignal(DomainModel):
    signal_id: NonEmpty
    node_id: NonEmpty
    metric: SignalMetric
    observed_value: float
    expected_min: float | None = None
    expected_max: float | None = None
    unit: str = ""
    severity: Severity = Severity.MEDIUM
    observed_at: datetime

    @field_validator("observed_at")
    @classmethod
    def observed_timestamp_must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("observed_at must include a timezone")
        return value

    @field_validator("expected_max")
    @classmethod
    def max_must_not_be_below_min(cls, value, info):
        expected_min = info.data.get("expected_min")
        if value is not None and expected_min is not None and value < expected_min:
            raise ValueError("expected_max cannot be below expected_min")
        return value


class BusinessImpact(DomainModel):
    impact_id: NonEmpty
    consumer_node_id: NonEmpty
    affected_asset: NonEmpty
    impact_type: ImpactType
    severity: Severity
    description: NonEmpty
