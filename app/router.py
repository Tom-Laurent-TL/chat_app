from fastapi import APIRouter
from app.shared.routing import auto_discover_routers

router = APIRouter()

# Automatically mount routers from direct sub-features
auto_discover_routers(router, __file__, __package__)
