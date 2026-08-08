from dotenv import load_dotenv
import os

load_dotenv()


class Settings:

    # ==========================================================
    # PostgreSQL
    # ==========================================================

    DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
    DB_PORT = os.getenv("POSTGRES_PORT", "5432")
    DB_NAME = os.getenv("POSTGRES_DB")
    DB_USER = os.getenv("POSTGRES_USER")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")

    # ==========================================================
    # Application
    # ==========================================================

    APP_NAME = os.getenv(
        "APP_NAME",
        "Enterprise Knowledge Graph"
    )

    DEBUG = os.getenv(
        "DEBUG",
        "False"
    ).lower() == "true"

    # ==========================================================
    # JWT Authentication
    # ==========================================================

    SECRET_KEY = os.getenv(
        "SECRET_KEY"
    )

    JWT_ALGORITHM = os.getenv(
        "JWT_ALGORITHM",
        "HS256"
    )

    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv(
            "ACCESS_TOKEN_EXPIRE_MINUTES",
            "60"
        )
    )

    # ==========================================================
    # Encryption
    # ==========================================================

    # Used for encrypting database passwords
    ENCRYPTION_KEY = os.getenv(
        "ENCRYPTION_KEY"
    )

    # ==========================================================
    # Neo4j
    # ==========================================================

    NEO4J_URI = os.getenv(
        "NEO4J_URI",
        "bolt://localhost:7687"
    )

    NEO4J_USERNAME = os.getenv(
        "NEO4J_USERNAME",
        "neo4j"
    )

    NEO4J_PASSWORD = os.getenv(
        "NEO4J_PASSWORD"
    )

    # ==========================================================
    # Grok / xAI
    # ==========================================================

    XAI_API_KEY = os.getenv(
        "XAI_API_KEY"
    )

    GROK_MODEL = os.getenv(
        "GROK_MODEL",
        "grok-3-mini"
    )

    XAI_BASE_URL = os.getenv(
        "XAI_BASE_URL",
        "https://api.x.ai/v1"
    )

    # ==========================================================
    # GraphRAG
    # ==========================================================

    GRAPHRAG_MAX_CONTEXT_NODES = int(
        os.getenv(
            "GRAPHRAG_MAX_CONTEXT_NODES",
            "30"
        )
    )

    GRAPHRAG_MAX_CONTEXT_RELATIONSHIPS = int(
        os.getenv(
            "GRAPHRAG_MAX_CONTEXT_RELATIONSHIPS",
            "50"
        )
    )

    # Number of tokens/characters is not enforced here.
    # This value controls how much graph context we send
    # to the LLM.

    GRAPHRAG_TEMPERATURE = float(
        os.getenv(
            "GRAPHRAG_TEMPERATURE",
            "0.2"
        )
    )


settings = Settings()