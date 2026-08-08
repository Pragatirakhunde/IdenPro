from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.project import router as project_router
from app.api.datasource import router as datasource_router
from app.api.knowledge_graph import router as knowledge_graph
from app.api.profiling import router as profiling_router

from app.database.base import Base
from app.database.connection import engine
from app.api.graph_rag import router as graph_rag
from app.api.chat import router as chat



# -----------------------------
# Create Database Tables
# -----------------------------
def create_tables():
    """
    Create all database tables.
    This runs only if tables don't already exist.
    """
    Base.metadata.create_all(bind=engine)


# -----------------------------
# Application Lifespan
# -----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 50)
    print("🚀 Starting DataMind AI Backend...")
    print("=" * 50)

    create_tables()

    print("✅ Database initialized successfully")

    yield

    print("=" * 50)
    print("🛑 Shutting down DataMind AI Backend...")
    print("=" * 50)


# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI(
    title="DataMind AI API",
    description="AI Powered Data Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan
)


# -----------------------------
# CORS Configuration
# -----------------------------
app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:8501",   # Streamlit
        "http://127.0.0.1:8501"
    ],

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Register Routers
# -----------------------------
app.include_router(auth_router)
app.include_router(project_router)
app.include_router(datasource_router)
app.include_router(knowledge_graph)
app.include_router(graph_rag)
app.include_router(chat)
app.include_router(profiling_router)

# -----------------------------
# Root Endpoint
# -----------------------------
@app.get("/", tags=["Home"])
def home():
    return {
        "application": "DataMind AI",
        "version": "1.0.0",
        "status": "Running"
    }


# -----------------------------
# Health Check
# -----------------------------
@app.get("/health", tags=["Health"])
def health():
    return {
        "status": "healthy"
    }