from app.database.connection import engine
from app.database.base import Base

# Import all models so SQLAlchemy knows about them
from app.models import User


def create_tables():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_tables()
    print("Database tables created successfully.")