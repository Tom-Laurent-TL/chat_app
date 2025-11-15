# App Module

This is the root application module following the Octopus architecture.

## Structure

- `main.py` - FastAPI application entry point
- `router.py` - Root router with auto-discovery
- `__init__.py` - Exports shared utilities (settings, auto_discover_routers)
- `features/` - Feature modules (add with `octopus add feature <name>`)
- `shared/` - Shared utilities (add with `octopus add shared <name>`)

## Default Shared Modules

- `shared/config/` - Application settings using pydantic-settings
- `shared/routing/` - Router auto-discovery utilities

## Adding Components

```bash
# Add a feature
octopus add feature users

# Add a shared module
octopus add shared database

# View structure
octopus structure
```

Each feature and shared module is a self-contained unit with its own:
- router.py (features only)
- service.py
- entities.py
- schemas.py
- features/ subdirectory (recursive)
- shared/ subdirectory (recursive)
