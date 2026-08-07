from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ============================================================
# Graph Node
# ============================================================

@dataclass
class GraphNode:
    """
    Represents a node in the knowledge graph.
    """

    id: str

    label: str

    node_type: str

    properties: dict[str, Any] = field(default_factory=dict)


# ============================================================
# Graph Edge
# ============================================================

@dataclass
class GraphEdge:
    """
    Represents a relationship between two nodes.
    """

    source: str

    target: str

    relationship: str

    properties: dict[str, Any] = field(default_factory=dict)


# ============================================================
# Knowledge Graph
# ============================================================

@dataclass
class KnowledgeGraph:

    nodes: list[GraphNode] = field(default_factory=list)

    edges: list[GraphEdge] = field(default_factory=list)


# ============================================================
# Entity Types
# ============================================================

class NodeType:

    DATABASE = "DATABASE"

    TABLE = "TABLE"

    COLUMN = "COLUMN"

    DATA_TYPE = "DATA_TYPE"

    PII = "PII"

    PATTERN = "PATTERN"

    QUALITY = "QUALITY"


# ============================================================
# Relationship Types
# ============================================================

class RelationType:

    HAS_TABLE = "HAS_TABLE"

    HAS_COLUMN = "HAS_COLUMN"

    HAS_DATA_TYPE = "HAS_DATA_TYPE"

    HAS_PATTERN = "HAS_PATTERN"

    HAS_PII = "HAS_PII"

    HAS_QUALITY = "HAS_QUALITY"

    REFERENCES = "REFERENCES"