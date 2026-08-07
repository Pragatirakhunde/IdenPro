from __future__ import annotations

from abc import abstractmethod
from pathlib import Path
from typing import List

import pandas as pd

from app.metadata.base_extractor import BaseExtractor
from app.metadata.models import (
    ColumnMetadata,
    ForeignKeyMetadata,
    IndexMetadata,
    MetadataResult,
    MetadataSummary,
    TableMetadata,
    ViewMetadata,
)


class BaseFileExtractor(BaseExtractor):
    """
    Base class for all file extractors.

    Child classes only need to implement:
        load_dataframe()

    Everything else (metadata extraction, profiling, PK detection,
    sample data, etc.) is handled here.
    """

    def __init__(self, file_path: str):

        super().__init__(file_path)

        self.file_path = Path(file_path)

        self.df: pd.DataFrame | None = None

    # =====================================================
    # Child Implementation
    # =====================================================

    @abstractmethod
    def load_dataframe(self) -> pd.DataFrame:
        pass

    # =====================================================
    # Connection
    # =====================================================

    def connect(self):

        self.df = self.load_dataframe()

        return self.df

    # =====================================================
    # Tables
    # =====================================================

    def extract_tables(self) -> List[TableMetadata]:

        if self.df is None:
            self.connect()

        table = TableMetadata(
            name=self.file_path.stem,
            row_count=len(self.df),
        )

        return [table]

    # =====================================================
    # Columns
    # =====================================================

    def extract_columns(
        self,
        table_name: str = "",
    ) -> List[ColumnMetadata]:

        if self.df is None:
            self.connect()

        columns = []

        for column in self.df.columns:

            series = self.df[column]

            metadata = ColumnMetadata(

                name=str(column),

                data_type=str(series.dtype),

                nullable=bool(series.isna().any()),

                unique=bool(series.is_unique),

                primary_key=False,

                foreign_key=False,

                default_value=None,

                max_length=None,

                comment=None,

                null_count=int(series.isna().sum()),

                null_percentage=round(

                    (series.isna().sum() / len(self.df)) * 100,

                    2,

                ) if len(self.df) else 0,

                unique_count=int(series.nunique()),

                sample_values=[
                    str(v)
                    for v in series.dropna().head(5).tolist()
                ],
            )

            columns.append(metadata)

        return columns

    # =====================================================
    # Primary Keys
    # =====================================================

    def extract_primary_keys(
        self,
        table_name: str = "",
    ) -> List[str]:

        if self.df is None:
            self.connect()

        keys = []

        total_rows = len(self.df)

        for column in self.df.columns:

            series = self.df[column]

            if (

                series.is_unique

                and series.isna().sum() == 0

                and len(series) == total_rows

            ):

                keys.append(str(column))

        return keys

    # =====================================================
    # Foreign Keys
    # =====================================================

    def extract_foreign_keys(
        self,
        table_name: str = "",
    ) -> List[ForeignKeyMetadata]:

        return []

    # =====================================================
    # Indexes
    # =====================================================

    def extract_indexes(
        self,
        table_name: str = "",
    ) -> List[IndexMetadata]:

        return []

    # =====================================================
    # Views
    # =====================================================

    def extract_views(self) -> List[ViewMetadata]:

        return []

    # =====================================================
    # Row Count
    # =====================================================

    def get_row_count(
        self,
        table_name: str = "",
    ) -> int:

        if self.df is None:
            self.connect()

        return len(self.df)

    # =====================================================
    # Sample Data
    # =====================================================

    def get_sample_data(
        self,
        table_name: str = "",
        limit: int = 5,
    ) -> list[dict]:

        if self.df is None:
            self.connect()

        return self.df.head(limit).to_dict(
            orient="records"
        )

    # =====================================================
    # Metadata
    # =====================================================

    def extract_metadata(self) -> MetadataResult:

        if self.df is None:
            self.connect()

        table = TableMetadata(

            name=self.file_path.stem,

            row_count=self.get_row_count(),

            columns=self.extract_columns(),

            primary_keys=self.extract_primary_keys(),

            foreign_keys=self.extract_foreign_keys(),

            indexes=self.extract_indexes(),

        )

        summary = MetadataSummary(

            total_tables=1,

            total_views=0,

            total_columns=len(table.columns),

            total_primary_keys=len(table.primary_keys),

            total_foreign_keys=len(table.foreign_keys),

            total_indexes=len(table.indexes),

            total_relationships=0,

        )

        return MetadataResult(

            tables=[table],

            relationships=[],

            views=self.extract_views(),

            summary=summary,

        )

    # =====================================================
    # File Information
    # =====================================================

    def get_file_information(self):

        if self.df is None:
            self.connect()

        return {

            "filename": self.file_path.name,

            "extension": self.file_path.suffix,

            "size_bytes": self.file_path.stat().st_size,

            "rows": len(self.df),

            "columns": len(self.df.columns),

            "memory_usage": int(

                self.df.memory_usage(
                    deep=True
                ).sum()

            ),

        }

    # =====================================================
    # Duplicate Rows
    # =====================================================

    def duplicate_rows(self) -> int:

        if self.df is None:
            self.connect()

        return int(self.df.duplicated().sum())

    # =====================================================
    # Missing Values
    # =====================================================

    def missing_value_summary(self):

        if self.df is None:
            self.connect()

        result = {}

        for column in self.df.columns:

            count = int(
                self.df[column].isna().sum()
            )

            percentage = round(

                (count / len(self.df)) * 100,

                2,

            ) if len(self.df) else 0

            result[column] = {

                "count": count,

                "percentage": percentage,

            }

        return result

    # =====================================================
    # Cleanup
    # =====================================================

    def close(self):

        self.df = None