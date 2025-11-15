#!/usr/bin/env python3
"""
Alembic Migration Reset Script for Chat App

A utility script for managing Alembic migration state:
- Reset migration history
- Stamp to specific revisions
- Check migration status
- Clean migration files

Usage:
    uv run python scripts/alembic_reset.py [command]

Commands:
    reset       - Reset to base revision (removes all migration history)
    stamp       - Stamp database to a specific revision
    current     - Show current migration revision
    history     - Show migration history
    clean       - Remove all migration files (dangerous!)
    init        - Reinitialize Alembic if needed

Environment Variables:
    DATABASE_URL - Database connection URL (uses app settings if not set)
"""

import os
import sys
from pathlib import Path
import shutil
import subprocess
from typing import Dict, Any

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.shared.database.service import engine
from app.shared.config.service import settings
from sqlalchemy import text


class AlembicManager:
    """Alembic migration management utilities."""

    def __init__(self):
        """Initialize the Alembic manager."""
        self.project_root = Path(__file__).parent.parent
        self.alembic_dir = self.project_root / "alembic"
        self.versions_dir = self.alembic_dir / "versions"

    def run_alembic_command(self, *args) -> Dict[str, Any]:
        """Run an Alembic command and return the result."""
        try:
            cmd = ["uv", "run", "alembic"] + list(args)
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def reset_to_base(self, confirm: bool = False) -> Dict[str, Any]:
        """Reset Alembic to base revision."""
        if not confirm:
            return {"error": "Confirmation required. Use --confirm flag."}

        print("🔄 Resetting Alembic to base revision...")

        # Stamp to base
        result = self.run_alembic_command("stamp", "base")
        if not result["success"]:
            return {"status": "failed", "error": result.get("stderr", "Unknown error")}

        print("✅ Alembic reset to base revision")
        return {"status": "reset", "message": "Alembic reset to base successfully"}

    def stamp_revision(self, revision: str) -> Dict[str, Any]:
        """Stamp database to a specific revision."""
        print(f"🏷️  Stamping database to revision: {revision}")

        result = self.run_alembic_command("stamp", revision)
        if not result["success"]:
            return {"status": "failed", "error": result.get("stderr", "Unknown error")}

        return {"status": "stamped", "revision": revision, "message": f"Stamped to {revision}"}

    def get_current_revision(self) -> Dict[str, Any]:
        """Get current migration revision."""
        result = self.run_alembic_command("current")

        if not result["success"]:
            return {"status": "failed", "error": result.get("stderr", "Unknown error")}

        current = result["stdout"].strip()
        return {"status": "success", "current_revision": current}

    def get_migration_history(self) -> Dict[str, Any]:
        """Get migration history."""
        result = self.run_alembic_command("history")

        if not result["success"]:
            return {"status": "failed", "error": result.get("stderr", "Unknown error")}

        return {"status": "success", "history": result["stdout"]}

    def clean_migrations(self, confirm: bool = False) -> Dict[str, Any]:
        """Remove all migration files (dangerous operation)."""
        if not confirm:
            return {"error": "Confirmation required. Use --confirm flag. This will delete all migration files!"}

        if not self.versions_dir.exists():
            return {"status": "no_action", "message": "No versions directory found"}

        print("🗑️  Removing all migration files...")

        # Remove all .py files in versions directory
        removed = []
        for file_path in self.versions_dir.glob("*.py"):
            if file_path.name != "__pycache__":
                file_path.unlink()
                removed.append(file_path.name)

        # Reset to base
        self.reset_to_base(confirm=True)

        return {
            "status": "cleaned",
            "message": f"Removed {len(removed)} migration files",
            "removed_files": removed
        }

    def reinitialize_alembic(self, confirm: bool = False) -> Dict[str, Any]:
        """Reinitialize Alembic (removes and recreates alembic directory)."""
        if not confirm:
            return {"error": "Confirmation required. Use --confirm flag. This will delete the entire alembic directory!"}

        if not self.alembic_dir.exists():
            return {"status": "no_action", "message": "No alembic directory found"}

        print("🔄 Reinitializing Alembic...")

        # Remove alembic directory
        shutil.rmtree(self.alembic_dir)

        # Reinitialize
        result = self.run_alembic_command("init", "alembic")
        if not result["success"]:
            return {"status": "failed", "error": result.get("stderr", "Failed to reinitialize")}

        # Update env.py
        env_py_path = self.alembic_dir / "env.py"
        if env_py_path.exists():
            self._update_env_py(env_py_path)

        return {"status": "reinitialized", "message": "Alembic reinitialized successfully"}

    def _update_env_py(self, env_py_path: Path):
        """Update the env.py file with proper imports."""
        env_content = env_py_path.read_text()

        # Add the necessary imports
        import_lines = '''# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
from app.shared.database.service import Base
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.
'''

        # Replace the placeholder
        env_content = env_content.replace(
            "# add your model's MetaData object here\n# for 'autogenerate' support\n# from myapp import mymodel\n# target_metadata = mymodel.Base.metadata\ntarget_metadata = None",
            import_lines
        )

        env_py_path.write_text(env_content)


def print_migration_status(manager: AlembicManager):
    """Print comprehensive migration status."""
    print("🔄 Alembic Migration Status")
    print("=" * 50)

    # Current revision
    current = manager.get_current_revision()
    if current["status"] == "success":
        revision = current.get("current_revision", "None")
        print(f"📍 Current Revision: {revision}")
    else:
        print(f"❌ Current revision error: {current.get('error', 'Unknown')}")

    # History
    history = manager.get_migration_history()
    if history["status"] == "success":
        print("\n📜 Migration History:")
        print(history["history"])
    else:
        print(f"❌ History error: {history.get('error', 'Unknown')}")

    # Check for pending migrations
    result = manager.run_alembic_command("check")
    if result["success"]:
        print("✅ No pending migrations")
    else:
        print("⚠️  Pending migrations detected")

    print("=" * 50)


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Alembic Migration Reset Script")
    parser.add_argument("command", choices=[
        "reset", "stamp", "current", "history", "clean", "init", "status"
    ], help="Command to execute")
    parser.add_argument("--confirm", action="store_true",
                       help="Confirm destructive operations")
    parser.add_argument("--revision", default="head",
                       help="Revision for stamp command (default: head)")

    args = parser.parse_args()

    manager = AlembicManager()

    commands = {
        "reset": lambda: print(manager.reset_to_base(args.confirm)),
        "stamp": lambda: print(manager.stamp_revision(args.revision)),
        "current": lambda: print(manager.get_current_revision()),
        "history": lambda: print(manager.get_migration_history()),
        "clean": lambda: print(manager.clean_migrations(args.confirm)),
        "init": lambda: print(manager.reinitialize_alembic(args.confirm)),
        "status": lambda: print_migration_status(manager)
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