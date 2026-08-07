import json
from pathlib import Path

import pandas as pd

from app.metadata.files.base_file_extractor import BaseFileExtractor
from app.metadata.models import (
    MetadataResult,
    MetadataSummary,
    TableMetadata,
)


class JSONExtractor(BaseFileExtractor):
    """
    Metadata extractor for JSON files.

    Supported formats:
        1. List of dictionaries
        2. Single dictionary
        3. Nested JSON
        4. API response JSON
    """

    def __init__(self, file_path: str):

        super().__init__(file_path)

        self.raw_json = None

    # =====================================================
    # Load JSON
    # =====================================================

    def load_dataframe(self):

        if not self.file_path.exists():

            raise FileNotFoundError(
                f"{self.file_path} not found."
            )

        with open(
            self.file_path,
            "r",
            encoding="utf-8",
        ) as f:

            self.raw_json = json.load(f)

        # ----------------------------
        # List of records
        # ----------------------------

        if isinstance(self.raw_json, list):

            df = pd.json_normalize(
                self.raw_json,
                sep="."
            )

        # ----------------------------
        # Dictionary
        # ----------------------------

        elif isinstance(self.raw_json, dict):

            # Common API pattern
            if "data" in self.raw_json and isinstance(
                self.raw_json["data"],
                list,
            ):

                df = pd.json_normalize(
                    self.raw_json["data"],
                    sep="."
                )

            else:

                df = pd.json_normalize(
                    self.raw_json,
                    sep="."
                )

        else:

            raise ValueError(
                "Unsupported JSON structure."
            )

        self.df = df

        return df

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
    # JSON Information
    # =====================================================

    def json_information(self):

        return {

            "filename": self.file_path.name,

            "extension": self.file_path.suffix,

            "rows": len(self.df),

            "columns": len(self.df.columns),

            "size_bytes": Path(
                self.file_path
            ).stat().st_size,

            "root_type": type(
                self.raw_json
            ).__name__,
        }

    # =====================================================
    # Close
    # =====================================================

    def close(self):

        self.df = None

        self.raw_json = None