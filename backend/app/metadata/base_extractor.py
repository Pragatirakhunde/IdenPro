from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from app.metadata.models import (
    ColumnMetadata,
    ForeignKeyMetadata,
    IndexMetadata,
    MetadataResult,
    TableMetadata,
    ViewMetadata,
)


class BaseExtractor(ABC):
    """
    Base interface implemented by every metadata extractor.

    File Sources
    ------------
    - CSV
    - Excel
    - JSON
    - XML
    - Parquet

    Database Sources
    ----------------
    - PostgreSQL
    - MySQL
    - SQLite
    - SQL Server
    - Oracle

    Every extractor must return strongly typed metadata objects.
    """

    def __init__(self, source):

        self.source = source

    # =====================================================
    # Connection
    # =====================================================

    @abstractmethod
    def connect(self):
        """Open the source."""
        raise NotImplementedError

    # =====================================================
    # Tables
    # =====================================================

    @abstractmethod
    def extract_tables(self) -> List[TableMetadata]:
        """
        Returns all tables discovered in the source.
        """
        raise NotImplementedError

    # =====================================================
    # Columns
    # =====================================================

    @abstractmethod
    def extract_columns(
        self,
        table_name: str,
    ) -> List[ColumnMetadata]:
        """
        Returns metadata for all columns of a table.
        """
        raise NotImplementedError

    # =====================================================
    # Primary Keys
    # =====================================================

    @abstractmethod
    def extract_primary_keys(
        self,
        table_name: str,
    ) -> List[str]:
        """
        Returns primary key column names.
        """
        raise NotImplementedError

    # =====================================================
    # Foreign Keys
    # =====================================================

    @abstractmethod
    def extract_foreign_keys(
        self,
        table_name: str,
    ) -> List[ForeignKeyMetadata]:
        """
        Returns foreign key metadata.
        """
        raise NotImplementedError

    # =====================================================
    # Indexes
    # =====================================================

    @abstractmethod
    def extract_indexes(
        self,
        table_name: str,
    ) -> List[IndexMetadata]:
        """
        Returns index metadata.
        """
        raise NotImplementedError

    # =====================================================
    # Views
    # =====================================================

    @abstractmethod
    def extract_views(self) -> List[ViewMetadata]:
        """
        Returns all database views.
        """
        raise NotImplementedError

    # =====================================================
    # Row Count
    # =====================================================

    @abstractmethod
    def get_row_count(
        self,
        table_name: str,
    ) -> int:
        """
        Returns number of rows.
        """
        raise NotImplementedError

    # =====================================================
    # Sample Data
    # =====================================================

    @abstractmethod
    def get_sample_data(
        self,
        table_name: str,
        limit: int = 5,
    ) -> list[dict]:
        """
        Returns sample records.

        Example
        -------
        [
            {
                "id": 1,
                "name": "Alice"
            }
        ]
        """
        raise NotImplementedError

    # =====================================================
    # Complete Metadata
    # =====================================================

    @abstractmethod
    def extract_metadata(self) -> MetadataResult:
        """
        Returns complete metadata for the source.
        """
        raise NotImplementedError

    # =====================================================
    # Cleanup
    # =====================================================

    @abstractmethod
    def close(self):
        """Release resources."""
        raise NotImplementedError