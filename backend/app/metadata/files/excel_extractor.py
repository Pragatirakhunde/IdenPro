from pathlib import Path

import pandas as pd
from app.metadata.files.base_file_extractor import BaseFileExtractor
from app.metadata.models import (
    MetadataResult,
    MetadataSummary,
    TableMetadata,
)


class ExcelExtractor(BaseFileExtractor):
    """
    Metadata extractor for Excel files.

    Each worksheet is treated as an independent table.
    """

    def __init__(self, file_path: str):

        super().__init__(file_path)

        self.workbook = None

        self.sheets: dict[str, pd.DataFrame] = {}

    # =====================================================
    # Load Workbook
    # =====================================================

    def load_dataframe(self):

        if not self.file_path.exists():

            raise FileNotFoundError(
                f"{self.file_path} not found."
            )

        self.workbook = pd.ExcelFile(self.file_path)

        for sheet in self.workbook.sheet_names:

            self.sheets[sheet] = pd.read_excel(
                self.file_path,
                sheet_name=sheet,
            )

        # Base class expects one dataframe.
        # Use first sheet as default.
        self.df = self.sheets[
            self.workbook.sheet_names[0]
        ]

        return self.df

    # =====================================================
    # Metadata
    # =====================================================

    def extract_metadata(self):

        if self.df is None:

            self.connect()

        tables = []

        total_columns = 0

        total_primary_keys = 0

        for sheet_name, dataframe in self.sheets.items():

            self.df = dataframe

            columns = self.extract_columns()

            primary_keys = self.extract_primary_keys()

            table = TableMetadata(

                name=sheet_name,

                row_count=len(dataframe),

                columns=columns,

                primary_keys=primary_keys,

                foreign_keys=[],

                indexes=[],
            )

            tables.append(table)

            total_columns += len(columns)

            total_primary_keys += len(primary_keys)

        self.df = self.sheets[
            self.workbook.sheet_names[0]
        ]

        summary = MetadataSummary(

            total_tables=len(tables),

            total_views=0,

            total_columns=total_columns,

            total_primary_keys=total_primary_keys,

            total_foreign_keys=0,

            total_indexes=0,

            total_relationships=0,
        )

        return MetadataResult(

            tables=tables,

            relationships=[],

            views=[],

            summary=summary,
        )

    # =====================================================
    # Workbook Information
    # =====================================================

    def workbook_information(self):

        return {

            "filename": self.file_path.name,

            "extension": self.file_path.suffix,

            "sheet_count": len(self.workbook.sheet_names),

            "sheet_names": self.workbook.sheet_names,

            "size_bytes": Path(
                self.file_path
            ).stat().st_size,
        }

    # =====================================================
    # Close
    # =====================================================

    def close(self):

        self.df = None

        self.sheets = {}

        self.workbook = None