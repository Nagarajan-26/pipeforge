from datetime import UTC, datetime

import networkx as nx
from pydantic import Field, model_validator

from pipeforge.models.entities import (
    BusinessImpact,
    DataQualitySignal,
    DomainModel,
    ExecutionEvent,
    FaultInjection,
    PipelineEdge,
    PipelineNode,
)
from pipeforge.models.enums import NodeType, TopologyType


class PipelineScenario(DomainModel):
    scenario_id: str = Field(min_length=1)
    seed: int
    topology: TopologyType
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    nodes: list[PipelineNode] = Field(min_length=2)
    edges: list[PipelineEdge] = Field(min_length=1)

    fault: FaultInjection
    execution_events: list[ExecutionEvent] = Field(default_factory=list)
    data_quality_signals: list[DataQualitySignal] = Field(default_factory=list)
    business_impacts: list[BusinessImpact] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_scenario_integrity(self):
        if self.created_at.tzinfo is None or self.created_at.utcoffset() is None:
            raise ValueError("created_at must include a timezone")

        node_ids = [node.node_id for node in self.nodes]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("Node IDs must be unique")

        known_nodes = set(node_ids)

        if self.fault.target_node_id not in known_nodes:
            raise ValueError("Fault target must reference an existing node")

        event_ids = [event.event_id for event in self.execution_events]
        if len(event_ids) != len(set(event_ids)):
            raise ValueError("Execution event IDs must be unique")

        signal_ids = [signal.signal_id for signal in self.data_quality_signals]
        if len(signal_ids) != len(set(signal_ids)):
            raise ValueError("Data quality signal IDs must be unique")

        impact_ids = [impact.impact_id for impact in self.business_impacts]
        if len(impact_ids) != len(set(impact_ids)):
            raise ValueError("Business impact IDs must be unique")

        for event in self.execution_events:
            if event.node_id not in known_nodes:
                raise ValueError(
                    f"Execution event {event.event_id} references unknown node {event.node_id}"
                )

        for signal in self.data_quality_signals:
            if signal.node_id not in known_nodes:
                raise ValueError(
                    f"Signal {signal.signal_id} references unknown node {signal.node_id}"
                )

        node_by_id = {node.node_id: node for node in self.nodes}
        for impact in self.business_impacts:
            if impact.consumer_node_id not in known_nodes:
                raise ValueError(
                    f"Impact {impact.impact_id} references "
                    f"unknown consumer {impact.consumer_node_id}"
                )
            if node_by_id[impact.consumer_node_id].node_type != NodeType.CONSUMER:
                raise ValueError(f"Impact {impact.impact_id} must reference a consumer node")

        graph = nx.DiGraph()
        graph.add_nodes_from(node_ids)

        for edge in self.edges:
            if edge.source_node_id not in known_nodes:
                raise ValueError(f"Edge references unknown source {edge.source_node_id}")
            if edge.target_node_id not in known_nodes:
                raise ValueError(f"Edge references unknown target {edge.target_node_id}")
            if edge.source_node_id == edge.target_node_id:
                raise ValueError("Self-referencing pipeline edges are invalid")
            if graph.has_edge(edge.source_node_id, edge.target_node_id):
                raise ValueError("Duplicate pipeline edges are not allowed")

            graph.add_edge(edge.source_node_id, edge.target_node_id)

        if not nx.is_directed_acyclic_graph(graph):
            raise ValueError("Pipeline dependency graph must be acyclic")

        return self

    def dependency_graph(self) -> nx.DiGraph:
        """Return a fresh graph representation of this scenario."""
        graph = nx.DiGraph()
        for node in self.nodes:
            graph.add_node(node.node_id, **node.model_dump(mode="json"))
        for edge in self.edges:
            graph.add_edge(
                edge.source_node_id,
                edge.target_node_id,
                relationship=edge.relationship,
            )
        return graph
