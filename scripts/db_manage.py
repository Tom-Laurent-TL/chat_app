#!/usr/bin/env python3
"""
Database Management Script for Chat App

A comprehensive script for database operations including:
- Table status and information
- Database reset/cleanup
- Migration status
- Connection testing
- Data seeding

Usage:
    uv run python scripts/db_manage.py [command]

Commands:
    status      - Show database status and table information
    reset       - Reset database (drop all tables and recreate)
    migrate     - Run pending migrations
    seed        - Seed database with test data
    clean       - Remove all data but keep tables
    test        - Test database connection
    info        - Show database configuration info

Environment Variables:
    DATABASE_URL - Database connection URL (uses app settings if not set)
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.shared.database.service import engine, Base, SessionLocal, DatabaseService
from app.shared.config.service import settings
from sqlalchemy import text


class DatabaseManager:
    """Database management utilities."""

    def __init__(self):
        """Initialize the database manager."""
        self.db_service = DatabaseService()
        self.engine = engine

    def get_table_info(self) -> Dict[str, Any]:
        """Get information about all tables in the database."""
        try:
            with self.engine.connect() as conn:
                # Get table names
                if self.engine.name == "sqlite":
                    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"))
                else:
                    result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))

                tables = [row[0] for row in result]

                table_info = {}
                for table_name in tables:
                    # Get row count
                    try:
                        count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                        row_count = count_result.scalar()
                    except:
                        row_count = "N/A"

                    table_info[table_name] = {
                        "row_count": row_count,
                        "exists": True
                    }

                return {
                    "tables": table_info,
                    "total_tables": len(tables),
                    "database_type": self.engine.name
                }

        except Exception as e:
            return {
                "error": str(e),
                "tables": {},
                "total_tables": 0,
                "database_type": self.engine.name
            }

    def test_connection(self) -> Dict[str, Any]:
        """Test database connection."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                conn.commit()
            return {"status": "connected", "healthy": True}
        except Exception as e:
            return {"status": "failed", "healthy": False, "error": str(e)}

    def reset_database(self, confirm: bool = False) -> Dict[str, Any]:
        """Reset the database by dropping and recreating all tables."""
        if not confirm:
            return {"error": "Confirmation required. Use --confirm flag."}

        try:
            print("🗑️  Dropping all tables...")
            Base.metadata.drop_all(bind=self.engine)

            print("📦 Creating all tables...")
            Base.metadata.create_all(bind=self.engine)

            return {"status": "reset", "message": "Database reset successfully"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def clean_data(self, confirm: bool = False) -> Dict[str, Any]:
        """Remove all data but keep table structures."""
        if not confirm:
            return {"error": "Confirmation required. Use --confirm flag."}

        try:
            table_info = self.get_table_info()
            tables = table_info.get("tables", {})

            with self.engine.connect() as conn:
                for table_name in tables:
                    if tables[table_name]["exists"]:
                        print(f"🧹 Cleaning table: {table_name}")
                        try:
                            conn.execute(text(f"DELETE FROM {table_name}"))
                            conn.commit()
                        except Exception as e:
                            print(f"⚠️  Failed to clean {table_name}: {e}")

            return {"status": "cleaned", "message": "Data cleaned successfully"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def run_migrations(self) -> Dict[str, Any]:
        """Run pending database migrations."""
        try:
            result = subprocess.run(
                ["uv", "run", "alembic", "upgrade", "head"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent
            )

            if result.returncode == 0:
                return {"status": "migrated", "message": "Migrations applied successfully"}
            else:
                return {"status": "failed", "error": result.stderr}

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status."""
        try:
            result = subprocess.run(
                ["uv", "run", "alembic", "current"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent
            )

            return {
                "current_revision": result.stdout.strip(),
                "status": "success" if result.returncode == 0 else "failed"
            }

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def seed_database(self, confirm: bool = False) -> Dict[str, Any]:
        """Seed database with test data."""
        if not confirm:
            return {"error": "Confirmation required. Use --confirm flag."}

        try:
            # Import seed data creation functions
            from scripts.seed_data import create_seed_data
            result = create_seed_data()
            return result

        except ImportError:
            return {"error": "Seed data script not found. Create scripts/seed_data.py first."}
        except Exception as e:
            return {"status": "failed", "error": str(e)}


def print_status_info(manager: DatabaseManager):
    """Print comprehensive database status information."""
    print("🗄️  Database Status Report")
    print("=" * 50)

    # Connection test
    conn_status = manager.test_connection()
    if conn_status["healthy"]:
        print("✅ Database connection: Healthy")
    else:
        print(f"❌ Database connection: Failed - {conn_status.get('error', 'Unknown error')}")
        return

    # Database info
    db_info = manager.db_service.get_connection_info()
    print(f"📊 Database Type: {db_info['engine_type']}")
    print(f"🔗 Connection Pool: {db_info['pool_size']} connections")
    print(f"⚙️  Environment: {db_info['environment']}")

    # Migration status
    migration_status = manager.get_migration_status()
    if migration_status["status"] == "success":
        revision = migration_status.get("current_revision", "None")
        print(f"🔄 Current Migration: {revision}")
    else:
        print("❌ Migration status: Failed to check")

    # Table information
    table_info = manager.get_table_info()
    if "error" in table_info:
        print(f"❌ Table info error: {table_info['error']}")
    else:
        print(f"📋 Tables: {table_info['total_tables']}")
        for table_name, info in table_info["tables"].items():
            row_count = info["row_count"]
            print(f"  • {table_name}: {row_count} rows")

    print("=" * 50)


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Database Management Script")
    parser.add_argument("command", choices=[
        "status", "reset", "migrate", "seed", "clean", "test", "info"
    ], help="Command to execute")
    parser.add_argument("--confirm", action="store_true",
                       help="Confirm destructive operations")

    args = parser.parse_args()

    manager = DatabaseManager()

    commands = {
        "status": lambda: print_status_info(manager),
        "reset": lambda: print(manager.reset_database(args.confirm)),
        "migrate": lambda: print(manager.run_migrations()),
        "seed": lambda: print(manager.seed_database(args.confirm)),
        "clean": lambda: print(manager.clean_data(args.confirm)),
        "test": lambda: print(manager.test_connection()),
        "info": lambda: print(manager.db_service.info())
    }

    try:
        result = commands[args.command]()
        if isinstance(result, dict) and result.get("status") == "failed":
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n🛑 Operation interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Operation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()