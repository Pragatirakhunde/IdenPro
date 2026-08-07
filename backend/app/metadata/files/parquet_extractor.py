from pathlib import Path

import pandas as pd

from app.metadata.files.base_file_extractor import BaseFileExtractor
from app.metadata.models import (
    MetadataResult,
    MetadataSummary,
    TableMetadata,
)


class ParquetExtractor(BaseFileExtractor):
    """
    Metadata extractor for Apache Parquet files.

    Features:
    - Supports .parquet files
    - Preserves native data types
    - Uses BaseFileExtractor for metadata generation
    """

    def __init__(self, file_path: str):

        super().__init__(file_path)

    # =====================================================
    # Load DataFrame
    # =====================================================

    def load_dataframe(self):

        if not self.file_path.exists():

            raise FileNotFoundError(
                f"{self.file_path} not found."
            )

        self.df = pd.read_parquet(self.file_path)

        return self.df

    # =====================================================
    # Metadata
    # =====================================================

    def extract_metadata(self):

        if self.df is None:

            self.connect()

        columns = self.extract_columns()

        primary_keys = self.extract_primary_keys()

        table = TableMetadata(

            name=self.file_path.stem,

            row_count=len(self.df),

            columns=columns,

            primary_keys=primary_keys,

            foreign_keys=[],

            indexes=[],
        )

        summary = MetadataSummary(

            total_tables=1,

            total_views=0,

            total_columns=len(columns),

            total_primary_keys=len(primary_keys),

            total_foreign_keys=0,

            total_indexes=0,

            total_relationships=0,
        )

        return MetadataResult(

            tables=[table],

            relationships=[],

            views=[],

            summary=summary,
        )

    # =====================================================
    # Parquet Information
    # =====================================================

    def parquet_information(self):

        return {

            "filename": self.file_path.name,

            "extension": self.file_path.suffix,

            "rows": len(self.df),

            "columns": len(self.df.columns),

            "memory_usage": int(
                self.df.memory_usage(
                    deep=True
                ).sum()
            ),

            "size_bytes": Path(
                self.file_path
            ).stat().st_size,

        }

    # =====================================================
    # Close
    # =====================================================

    def close(self):

        self.df = None