from __future__ import annotations

import os
from typing import Any

from neo4j import Driver, GraphDatabase
from dotenv import load_dotenv


load_dotenv()


class Neo4jClient:
    """
    Manages the Neo4j database connection.

    Environment variables:

        NEO4J_URI
        NEO4J_USERNAME
        NEO4J_PASSWORD
        NEO4J_DATABASE

    Example:

        NEO4J_URI=bolt://localhost:7687
        NEO4J_USERNAME=neo4j
        NEO4J_PASSWORD=password
        NEO4J_DATABASE=neo4j
    """

    def __init__(
        self,
        uri: str | None = None,
        username: str | None = None,
        password: str | None = None,
        database: str | None = None,
    ):

        self.uri = (
            uri
            or os.getenv(
                "NEO4J_URI",
                "bolt://localhost:7687",
            )
        )

        self.username = (
            username
            or os.getenv(
                "NEO4J_USERNAME",
                "neo4j",
            )
        )

        self.password = (
            password
            or os.getenv(
                "NEO4J_PASSWORD",
                "",
            )
        )

        self.database = (
            database
            or os.getenv(
                "NEO4J_DATABASE",
                "neo4j",
            )
        )

        self._driver: Driver | None = None

    # =====================================================
    # Connection
    # =====================================================

    def connect(self) -> Driver:
        """
        Create and return the Neo4j driver.
        """

        if self._driver is not None:
            return self._driver

        if not self.password:
            raise ValueError(
                "NEO4J_PASSWORD is not configured."
            )

        self._driver = GraphDatabase.driver(
            self.uri,
            auth=(
                self.username,
                self.password,
            ),
        )

        return self._driver

    # =====================================================
    # Driver
    # =====================================================

    @property
    def driver(self) -> Driver:
        """
        Return an active Neo4j driver.
        """

        if self._driver is None:
            self.connect()

        return self._driver

    # =====================================================
    # Verify Connection
    # =====================================================

    def verify_connection(self) -> bool:
        """
        Verify that Neo4j is reachable.
        """

        try:

            self.driver.verify_connectivity()

            return True

        except Exception:

            return False

    # =====================================================
    # Execute Query
    # =====================================================

    def execute(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Execute a Cypher query and return records as dictionaries.
        """

        parameters = parameters or {}

        with self.driver.session(
            database=self.database
        ) as session:

            result = session.run(
                query,
                parameters,
            )

            return [
                record.data()
                for record in result
            ]

    # =====================================================
    # Execute Write
    # =====================================================

    def execute_write(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Execute a write transaction.
        """

        parameters = parameters or {}

        def transaction(tx):

            result = tx.run(
                query,
                parameters,
            )

            return [
                record.data()
                for record in result
            ]

        with self.driver.session(
            database=self.database
        ) as session:

            return session.execute_write(
                transaction
            )

    # =====================================================
    # Execute Read
    # =====================================================

    def execute_read(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Execute a read transaction.
        """

        parameters = parameters or {}

        def transaction(tx):

            result = tx.run(
                query,
                parameters,
            )

            return [
                record.data()
                for record in result
            ]

        with self.driver.session(
            database=self.database
        ) as session:

            return session.execute_read(
                transaction
            )

    # =====================================================
    # Database Information
    # =====================================================

    def database_info(self) -> dict[str, Any]:
        """
        Return basic Neo4j database information.
        """

        query = """
        CALL dbms.components()
        YIELD name, versions, edition
        RETURN name, versions, edition
        """

        result = self.execute_read(
            query
        )

        if not result:

            return {}

        return result[0]

    # =====================================================
    # Close
    # =====================================================

    def close(self) -> None:
        """
        Close the Neo4j driver.
        """

        if self._driver is not None:

            self._driver.close()

            self._driver = None

    # =====================================================
    # Context Manager
    # =====================================================

    def __enter__(self):

        self.connect()

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):

        self.close()