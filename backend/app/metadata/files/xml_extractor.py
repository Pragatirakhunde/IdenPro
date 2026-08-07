from pathlib import Path

import pandas as pd
import xml.etree.ElementTree as ET

from app.metadata.files.base_file_extractor import BaseFileExtractor
from app.metadata.models import (
    MetadataResult,
    MetadataSummary,
    TableMetadata,
)


class XMLExtractor(BaseFileExtractor):
    """
    Metadata extractor for XML files.

    Supports:

    - Simple XML
    - Nested XML
    - Repeating records
    """

    def __init__(self, file_path: str):

        super().__init__(file_path)

        self.tree = None
        self.root = None

    # =====================================================
    # Convert XML Element -> Dictionary
    # =====================================================

    def _element_to_dict(self, element):

        data = {}

        # XML attributes
        for key, value in element.attrib.items():
            data[f"@{key}"] = value

        children = list(element)

        if not children:

            text = element.text.strip() if element.text else ""

            if text:
                data[element.tag] = text

            return data

        for child in children:

            if len(child):

                data[child.tag] = self._element_to_dict(child)

            else:

                data[child.tag] = child.text

        return data

    # =====================================================
    # Load XML
    # =====================================================

    def load_dataframe(self):

        if not self.file_path.exists():

            raise FileNotFoundError(
                f"{self.file_path} not found."
            )

        self.tree = ET.parse(self.file_path)

        self.root = self.tree.getroot()

        # ----------------------------------------------
        # Detect repeating child elements
        # ----------------------------------------------

        children = list(self.root)

        if not children:

            raise ValueError(
                "No records found in XML."
            )

        records = []

        for child in children:

            record = self._element_to_dict(child)

            records.append(record)

        df = pd.json_normalize(
            records,
            sep="."
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
    # XML Information
    # =====================================================

    def xml_information(self):

        return {

            "filename": self.file_path.name,

            "extension": self.file_path.suffix,

            "root_tag": self.root.tag,

            "rows": len(self.df),

            "columns": len(self.df.columns),

            "size_bytes": Path(
                self.file_path
            ).stat().st_size,

        }

    # =====================================================
    # Close
    # =====================================================

    def close(self):

        self.df = None
        self.tree = None
        self.root = None