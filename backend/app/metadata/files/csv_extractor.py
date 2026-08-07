from pathlib import Path

import pandas as pd
from app.metadata.files.base_file_extractor import BaseFileExtractor


class CSVExtractor(BaseFileExtractor):
    """
    Metadata extractor for CSV files.

    Responsibilities:
    - Read CSV into pandas DataFrame
    - Handle encoding fallback
    - Let BaseFileExtractor perform metadata extraction
    """

    SUPPORTED_ENCODINGS = [
        "utf-8",
        "utf-8-sig",
        "latin-1",
        "cp1252",
    ]

    def __init__(
        self,
        file_path: str,
        delimiter: str | None = None,
    ):

        super().__init__(file_path)

        self.delimiter = delimiter

    # =====================================================
    # Load DataFrame
    # =====================================================

    def load_dataframe(self) -> pd.DataFrame:

        if not self.file_path.exists():

            raise FileNotFoundError(
                f"File not found: {self.file_path}"
            )

        last_error = None

        for encoding in self.SUPPORTED_ENCODINGS:

            try:

                df = pd.read_csv(

                    self.file_path,

                    encoding=encoding,

                    sep=self.delimiter,

                    low_memory=False,

                )

                self.encoding = encoding

                return df

            except Exception as e:

                last_error = e

        raise ValueError(

            f"Unable to read CSV file.\n{last_error}"

        )

    # =====================================================
    # CSV Information
    # =====================================================

    def csv_information(self):

        return {

            "encoding": getattr(
                self,
                "encoding",
                "Unknown",
            ),

            "delimiter": self.delimiter or ",",

            "rows": len(self.df),

            "columns": len(self.df.columns),

            "file_size": Path(
                self.file_path
            ).stat().st_size,

        }