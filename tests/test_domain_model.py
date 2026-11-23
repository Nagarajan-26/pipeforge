from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from pipeforge.models import (
    BusinessImpact,
    DataQualitySignal,
    EventStatus,
    ExecutionEvent,
    FaultInjection,
    FaultType,
    ImpactType,
    NodeType,
    PipelineEdge,
    PipelineNode,
    PipelineScenario,
    Severity,
    SignalMetric,
    TopologyType,
)

UTC = UTC
NOW = datetime(2026, 11, 23, 10, 0, tzinfo=UTC)


def make_node(node_id, node_type):
    return PipelineNode(
        node_id=node_id,
        name=node_id.replace("_", " ").title(),
        node_type=node_type,
        system="synthetic_warehouse",
    )


def make_scenario(**overrides):
    values = {
        "scenario_id": "PF-ING-001",
        "seed": 42,
        "topology": TopologyType.LINEAR,
        "created_at": NOW,
        "nodes": [
            make_node("source_orders", NodeType.SOURCE),
            make_node("load_orders", NodeType.TRANSFORMATION),
            make_node("orders_mart", NodeType.CONSUMER),
        ],
        "edges": [
            PipelineEdge(
                source_node_id="source_orders",
                target_node_id="load_orders",
            ),
            PipelineEdge(
                source_node_id="load_orders",
                target_node_id="orders_mart",
            ),
        ],
        "fault": FaultInjection(
            fault_id="FAULT-001",
            fault_type=FaultType.INGESTION_FAILURE,
            target_node_id="source_orders",
            injected_at=NOW,
            description="Source ingestion stopped unexpectedly",
        ),
        "execution_events": [
            ExecutionEvent(
                event_id="EVENT-001",
                node_id="source_orders",
                status=EventStatus.FAILED,
                started_at=NOW,
                ended_at=NOW + timedelta(minutes=5),
                message="Ingestion job failed",
            )
        ],
        "data_quality_signals": [
            DataQualitySignal(
                signal_id="SIGNAL-001",
                node_id="source_orders",
                metric=SignalMetric.ROW_COUNT,
                observed_value=0,
                expected_min=1000,
                expected_max=5000,
                unit="rows",
                severity=Severity.HIGH,
                observed_at=NOW + timedelta(minutes=5),
            )
        ],
        "business_impacts": [
            BusinessImpact(
                impact_id="IMPACT-001",
                consumer_node_id="orders_mart",
                affected_asset="daily_sales_dashboard",
                impact_type=ImpactType.STALE_DATA,
                severity=Severity.HIGH,
                description="Dashboard is based on stale order data",
            )
        ],
    }
    values.update(overrides)
    return PipelineScenario(**values)


def test_valid_scenario_is_created():
    scenario = make_scenario()

    assert scenario.scenario_id == "PF-ING-001"
    assert scenario.seed == 42
    assert scenario.dependency_graph().number_of_nodes() == 3
    assert scenario.dependency_graph().number_of_edges() == 2


def test_dependency_graph_preserves_direction():
    graph = make_scenario().dependency_graph()

    assert graph.has_edge("source_orders", "load_orders")
    assert graph.has_edge("load_orders", "orders_mart")
    assert not graph.has_edge("orders_mart", "source_orders")


def test_duplicate_node_ids_are_rejected():
    nodes = [
        make_node("source_orders", NodeType.SOURCE),
        make_node("source_orders", NodeType.TRANSFORMATION),
    ]

    with pytest.raises(ValidationError, match="Node IDs must be unique"):
        make_scenario(nodes=nodes)


def test_unknown_fault_target_is_rejected():
    fault = FaultInjection(
        fault_id="FAULT-002",
        fault_type=FaultType.SCHEMA_DRIFT,
        target_node_id="missing_node",
        injected_at=NOW,
        description="Schema changed",
    )

    with pytest.raises(ValidationError, match="Fault target"):
        make_scenario(fault=fault)


def test_cyclic_dependency_graph_is_rejected():
    edges = [
        PipelineEdge(
            source_node_id="source_orders",
            target_node_id="load_orders",
        ),
        PipelineEdge(
            source_node_id="load_orders",
            target_node_id="orders_mart",
        ),
        PipelineEdge(
            source_node_id="orders_mart",
            target_node_id="source_orders",
        ),
    ]

    with pytest.raises(ValidationError, match="must be acyclic"):
        make_scenario(edges=edges)


def test_unknown_event_node_is_rejected():
    event = ExecutionEvent(
        event_id="EVENT-002",
        node_id="missing_node",
        status=EventStatus.FAILED,
        started_at=NOW,
    )

    with pytest.raises(ValidationError, match="unknown node"):
        make_scenario(execution_events=[event])


def test_impact_must_reference_consumer_node():
    impact = BusinessImpact(
        impact_id="IMPACT-002",
        consumer_node_id="load_orders",
        affected_asset="orders_mart",
        impact_type=ImpactType.STALE_DATA,
        severity=Severity.HIGH,
        description="Incorrectly attached to a transformation node",
    )

    with pytest.raises(ValidationError, match="must reference a consumer"):
        make_scenario(business_impacts=[impact])


def test_naive_fault_timestamp_is_rejected():
    with pytest.raises(ValidationError, match="timezone"):
        FaultInjection(
            fault_id="FAULT-003",
            fault_type=FaultType.INGESTION_FAILURE,
            target_node_id="source_orders",
            injected_at=datetime(2026, 11, 23, 10, 0),
            description="Missing timezone",
        )


def test_execution_end_before_start_is_rejected():
    with pytest.raises(ValidationError, match="ended_at"):
        ExecutionEvent(
            event_id="EVENT-003",
            node_id="source_orders",
            status=EventStatus.FAILED,
            started_at=NOW,
            ended_at=NOW - timedelta(minutes=1),
        )


def test_duplicate_edges_are_rejected():
    edge = PipelineEdge(
        source_node_id="source_orders",
        target_node_id="load_orders",
    )

    with pytest.raises(ValidationError, match="Duplicate pipeline edges"):
        make_scenario(edges=[edge, edge])


def test_unknown_signal_node_is_rejected():
    signal = DataQualitySignal(
        signal_id="SIGNAL-002",
        node_id="missing_node",
        metric=SignalMetric.ROW_COUNT,
        observed_value=0,
        observed_at=NOW,
    )

    with pytest.raises(ValidationError, match="unknown node"):
        make_scenario(data_quality_signals=[signal])
