# 🧩 Shared Module: Routing

Provides utilities, configuration, entities, and schemas shared across features.

## Usage
Features in the same Octopus app can import this module directly:
```python
from app.shared.routing.service import RoutingService
from app.shared.routing.entities import *
from app.shared.routing.schemas import *
```

## Structure
- `service.py` → reusable logic
- `entities.py` → ORM/domain entities
- `schemas.py` → Pydantic models
- `features/` → optional nested features
- `shared/` → optional sub-shared modules

Refer to `/docs` for architecture details.
