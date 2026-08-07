from app.metadata.database.sqlite_extractor import (
    SQLiteExtractor,
)


class DBConnection:

    database_name = (
        "sample_data/company.db"
    )

    username = ""
    password = ""
    host = ""
    port = ""


extractor = SQLiteExtractor(
    DBConnection()
)


print(
    "Connection:",
    extractor.test_connection()
)


metadata = extractor.extract_metadata()


print("\nSUMMARY")
print(
    metadata.summary
)


print("\nTABLES")

for table in metadata.tables:

    print(
        "\nTable:",
        table.name
    )

    print(
        "Rows:",
        table.row_count
    )


    print(
        "Columns:"
    )

    for column in table.columns:

        print(
            "  ",
            column.name,
            column.data_type
        )


print("\nRELATIONSHIPS")

for relation in metadata.relationships:

    print(
        relation
    )


extractor.close()