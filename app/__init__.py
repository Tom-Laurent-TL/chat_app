# Import shared modules to make them available throughout the app
from app.shared.config import settings
from app.shared.routing import auto_discover_routers

__all__ = ["settings", "auto_discover_routers"]
