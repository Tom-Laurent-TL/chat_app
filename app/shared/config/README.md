# 🧩 Shared Module: Config

Provides utilities, configuration, entities, and schemas shared across features.

## Usage
Features in the same Octopus app can import this module directly:
```python
from app.shared.config.service import ConfigService
from app.shared.config.entities import *
from app.shared.config.schemas import *
```

## Structure
- `service.py` → reusable logic
- `entities.py` → ORM/domain entities
- `schemas.py` → Pydantic models
- `features/` → optional nested features
- `shared/` → optional sub-shared modules

Refer to `/docs` for architecture details.
