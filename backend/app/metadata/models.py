from dataclasses import dataclass, field
from typing import List, Optional


# ==========================================================
# Column Metadata
# ==========================================================

@dataclass
class PrimaryKey:
    column_name: str

@dataclass
class ForeignKey:
    column_name: str
    referenced_table: str
    referenced_column: str



@dataclass
class ColumnMetadata:
    name: str
    data_type: str
    nullable: bool
    unique: bool = False
    primary_key: bool = False
    foreign_key: bool = False
    default_value: Optional[str] = None
    max_length: Optional[int] = None
    comment: Optional[str] = None

    # Profiling (filled later)
    null_count: int = 0
    null_percentage: float = 0.0
    unique_count: int = 0
    sample_values: List[str] = field(default_factory=list)


# ==========================================================
# Foreign Key Metadata
# ==========================================================

@dataclass
class ForeignKeyMetadata:
    column_name: str
    referenced_table: str
    referenced_column: str
    constraint_name: Optional[str] = None


# ==========================================================
# Index Metadata
# ==========================================================

@dataclass
class IndexMetadata:
    name: str
    columns: List[str]
    unique: bool = False


# ==========================================================
# Table Metadata
# ==========================================================

@dataclass
class TableMetadata:
    table_name: str
    schema: Optional[str] = None

    row_count: int = 0

    columns: List[ColumnMetadata] = field(default_factory=list)

    primary_keys: List[str] = field(default_factory=list)

    foreign_keys: List[ForeignKeyMetadata] = field(default_factory=list)

    indexes: List[IndexMetadata] = field(default_factory=list)

    comment: Optional[str] = None


# ==========================================================
# View Metadata
# ==========================================================

@dataclass
class ViewMetadata:
    name: str
    definition: Optional[str] = None


# ==========================================================
# Relationship Metadata
# ==========================================================

@dataclass
class RelationshipMetadata:
    source_table: str
    source_column: str

    target_table: str
    target_column: str

    relationship_type: str

    confidence_score: float = 1.0

    discovered_by: str = "foreign_key"


# ==========================================================
# Metadata Summary
# ==========================================================

@dataclass
class MetadataSummary:
    total_tables: int = 0
    total_views: int = 0
    total_columns: int = 0
    total_primary_keys: int = 0
    total_foreign_keys: int = 0
    total_indexes: int = 0
    total_relationships: int = 0


# ==========================================================
# Complete Metadata Result
# ==========================================================

@dataclass
class MetadataResult:
    tables: List[TableMetadata] = field(default_factory=list)

    views: List[ViewMetadata] = field(default_factory=list)

    relationships: List[RelationshipMetadata] = field(default_factory=list)

    summary: MetadataSummary = field(
        default_factory=MetadataSummary
    )

@dataclass
class ForeignKeyMetadata:
    """
    Represents foreign key relationship.
    """

    column_name: str

    referenced_table: str

    referenced_column: str



@dataclass
class PrimaryKeyMetadata:
    """
    Represents primary key information.
    """

    column_name: str