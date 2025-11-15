"""
Shared service for database.
Provides SQLAlchemy engine, session management, and database utilities.
"""
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from app.shared.config.service import settings


# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url or "sqlite:///./test.db",
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.environment == "development"
)

# Session factory for database connections
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all database models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database sessions.

    Yields a database session that will be automatically closed after use.
    Use with FastAPI's Depends(get_db) for dependency injection.

    Example:
        @router.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database tables.

    Creates all tables defined in the models that inherit from Base.
    Call this during application startup.

    Example:
        from app.shared.database.service import init_db

        @app.on_event("startup")
        def startup():
            init_db()
    """
    # Import all models here to ensure they're registered with SQLAlchemy
    # This prevents "table not found" errors
    try:
        # Import feature models dynamically if they exist
        from app.features import users
        from app.features import conversations
        # Add more feature imports as they are implemented
    except ImportError:
        # Features may not exist yet during initial setup
        pass

    Base.metadata.create_all(bind=engine)


def reset_db() -> None:
    """
    Reset database by dropping and recreating all tables.

    WARNING: This will delete all data! Use only in development/testing.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


class DatabaseService:
    """Utility service for database operations and information."""

    def __init__(self):
        """Initialize database service."""
        pass

    def get_connection_info(self) -> dict:
        """Get database connection information."""
        return {
            "database_url": settings.database_url or "sqlite:///./app.db",
            "engine_type": engine.name,
            "pool_size": getattr(engine.pool, 'size', lambda: 10)() if hasattr(engine.pool, 'size') else 10,
            "environment": settings.environment
        }

    def health_check(self) -> dict:
        """Perform a basic database health check."""
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                conn.commit()  # Ensure the connection works
            return {"status": "healthy", "database": "connected"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def info(self) -> dict:
        """Return information about the database shared module."""
        return {
            "message": "Shared database module is ready",
            "connection_info": self.get_connection_info(),
            "health": self.health_check()
        }
