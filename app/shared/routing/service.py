"""
Shared routing utilities.
Provides centralized auto-discovery for feature routers.
"""
import importlib
import pkgutil
from pathlib import Path
from typing import Optional
from fastapi import APIRouter


def auto_discover_routers(
    parent_router: APIRouter,
    current_module_file: str,
    current_package: Optional[str],
    verbose: bool = False
) -> None:
    """
    Automatically discover and mount routers from sub-features.
    
    This function scans the 'features/' subdirectory relative to the calling module
    and automatically includes any routers found in sub-feature modules.
    
    Args:
        parent_router: The APIRouter instance to mount discovered routers onto
        current_module_file: Pass __file__ from the calling module
        current_package: Pass __package__ from the calling module (for relative imports)
        verbose: If True, print discovery information (useful for debugging)
    
    Example:
        from fastapi import APIRouter
        from app.shared.routing import auto_discover_routers
        
        router = APIRouter(prefix="/users", tags=["users"])
        
        # ... add your routes ...
        
        # Automatically mount sub-feature routers
        auto_discover_routers(router, __file__, __package__)
    
    This eliminates the need for manual router registration and ensures
    consistent behavior across all nesting levels.
    """
    # Resolve the features directory relative to the calling module
    current_dir = Path(current_module_file).parent
    features_path = current_dir / "features"
    
    # Only proceed if features directory exists
    if not features_path.exists():
        if verbose:
            print(f"[Routing] No features directory at: {features_path}")
        return
    
    if verbose:
        print(f"[Routing] Discovering features in: {features_path}")
    
    # Iterate through all modules in the features directory
    for _, module_name, is_pkg in pkgutil.iter_modules([str(features_path)]):
        if not is_pkg:
            # Skip non-package modules
            if verbose:
                print(f"[Routing] Skipping non-package: {module_name}")
            continue
        
        try:
            # Import the router module using relative imports
            if current_package:
                module = importlib.import_module(
                    f".features.{module_name}.router",
                    package=current_package
                )
            else:
                # Fallback for root-level imports
                module = importlib.import_module(f"features.{module_name}.router")
            
            # Check if the module has a router attribute
            if not hasattr(module, "router"):
                if verbose:
                    print(f"[Routing] Warning: {module_name}.router has no 'router' attribute")
                continue
            
            # Mount the discovered router
            parent_router.include_router(module.router)
            
            if verbose:
                print(f"[Routing] ✓ Mounted: {module_name}")
        
        except ModuleNotFoundError as e:
            if verbose:
                print(f"[Routing] Module not found: {module_name} - {e}")
        
        except AttributeError as e:
            if verbose:
                print(f"[Routing] Attribute error in {module_name}: {e}")
        
        except Exception as e:
            # Catch any other errors to prevent one bad feature from breaking all discovery
            if verbose:
                print(f"[Routing] Error loading {module_name}: {type(e).__name__}: {e}")


class RoutingService:
    """Service for routing utilities and information."""
    
    def info(self) -> dict:
        """Return information about the routing module."""
        return {
            "message": "Shared routing module is ready.",
            "provides": ["auto_discover_routers"]
        }
