from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.shared.database.service import get_db
from app.shared.routing import auto_discover_routers
from .service import BotsService
from .schemas import (
    BotCreate, BotUpdate, BotResponse, BotListResponse, BotsStatusResponse
)

router = APIRouter(prefix="/bots", tags=["bots"])

service_dependency = lambda db=Depends(get_db): BotsService(db)


@router.get("/status", response_model=BotsStatusResponse)
def get_status(service: BotsService = Depends(service_dependency)):
    """Get status of the bots feature."""
    return service.status()


@router.post("/", response_model=BotResponse, status_code=201)
def create_bot(
    bot_data: BotCreate,
    created_by_id: int | None = None,  # For testing - should come from auth
    service: BotsService = Depends(service_dependency)
):
    """Create a new bot."""
    # TODO: Get current user ID from authentication context
    # For now, we'll use a placeholder user ID or the provided one for testing
    user_id = created_by_id or 1

    try:
        bot = service.create_bot(bot_data, user_id)
        return BotResponse.model_validate(bot)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=BotListResponse)
def list_bots(
    skip: int = Query(0, ge=0, description="Number of bots to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of bots to return"),
    active_only: bool = Query(False, description="Only return active bots"),
    service: BotsService = Depends(service_dependency)
):
    """List bots with pagination."""
    bots = service.list_bots(skip=skip, limit=limit, active_only=active_only)
    total = service.get_total_bots(active_only=active_only)

    # Convert bots to response format
    bot_responses = [BotResponse.model_validate(bot) for bot in bots]

    return BotListResponse(
        bots=bot_responses,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/public", response_model=BotListResponse)
def list_public_bots(
    skip: int = Query(0, ge=0, description="Number of bots to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of bots to return"),
    service: BotsService = Depends(service_dependency)
):
    """List public bots that anyone can use."""
    bots = service.get_public_bots(skip=skip, limit=limit)
    total = len(bots)  # For simplicity, just return the count of results

    # Convert bots to response format
    bot_responses = [BotResponse.model_validate(bot) for bot in bots]

    return BotListResponse(
        bots=bot_responses,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/my", response_model=BotListResponse)
def list_my_bots(
    skip: int = Query(0, ge=0, description="Number of bots to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of bots to return"),
    user_id: int | None = None,  # For testing - should come from auth
    service: BotsService = Depends(service_dependency)
):
    """List bots created by the current user."""
    # TODO: Get current user ID from authentication context
    current_user_id = user_id or 1

    bots = service.get_user_bots(current_user_id, skip=skip, limit=limit)
    total = service.get_total_bots(user_id=current_user_id)

    # Convert bots to response format
    bot_responses = [BotResponse.model_validate(bot) for bot in bots]

    return BotListResponse(
        bots=bot_responses,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{bot_id}", response_model=BotResponse)
def get_bot(
    bot_id: int,
    service: BotsService = Depends(service_dependency)
):
    """Get a bot by ID."""
    bot = service.get_bot(bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail=f"Bot with id {bot_id} not found")

    return BotResponse.model_validate(bot)


@router.get("/name/{bot_name}", response_model=BotResponse)
def get_bot_by_name(
    bot_name: str,
    service: BotsService = Depends(service_dependency)
):
    """Get a bot by name."""
    bot = service.get_bot_by_name(bot_name)
    if not bot:
        raise HTTPException(status_code=404, detail=f"Bot with name '{bot_name}' not found")

    return BotResponse.model_validate(bot)


@router.put("/{bot_id}", response_model=BotResponse)
def update_bot(
    bot_id: int,
    bot_data: BotUpdate,
    user_id: int | None = None,  # For testing - should come from auth
    service: BotsService = Depends(service_dependency)
):
    """Update a bot (only by the creator)."""
    # TODO: Get current user ID from authentication context
    current_user_id = user_id or 1

    try:
        bot = service.update_bot(bot_id, bot_data, current_user_id)
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found or access denied")
        return BotResponse.model_validate(bot)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{bot_id}", status_code=204)
def delete_bot(
    bot_id: int,
    user_id: int | None = None,  # For testing - should come from auth
    service: BotsService = Depends(service_dependency)
):
    """Delete a bot (soft delete, only by the creator)."""
    # TODO: Get current user ID from authentication context
    current_user_id = user_id or 1

    if not service.delete_bot(bot_id, current_user_id):
        raise HTTPException(status_code=404, detail="Bot not found or access denied")


# Automatically mount sub-feature routers
auto_discover_routers(router, __file__, __package__)
