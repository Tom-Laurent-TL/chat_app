from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.shared.database.service import get_db
from app.shared.routing import auto_discover_routers
from .service import MessagesService
from .schemas import (
    MessageCreate, MessageUpdate, MessageResponse, MessageWithSenderResponse, MessagesStatusResponse
)

router = APIRouter(
    prefix="/messages",
    tags=["messages"],
    dependencies=[Depends(get_db)]
)

service_dependency = lambda db=Depends(get_db): MessagesService(db)


@router.get("/status", response_model=MessagesStatusResponse)
def get_status(service: MessagesService = Depends(service_dependency)):
    """Get status of the messages feature."""
    return service.status()


@router.post("/", response_model=MessageResponse, status_code=201)
async def create_message(
    message_data: MessageCreate,
    sender_id: int | None = None,  # For testing - should come from auth
    service: MessagesService = Depends(service_dependency)
):
    """Create a new message."""
    # TODO: Get current user ID from authentication context
    # For now, we'll use a placeholder user ID or the provided one for testing
    user_id = sender_id or 1

    message = await service.create_message(message_data, user_id)
    return MessageResponse.model_validate(message)


@router.get("/conversation/{conversation_id}", response_model=List[MessageWithSenderResponse])
def get_conversation_messages(
    conversation_id: int,
    limit: int = Query(50, ge=1, le=100, description="Number of messages to return"),
    offset: int = Query(0, ge=0, description="Number of messages to skip"),
    service: MessagesService = Depends(service_dependency)
):
    """Get messages for a specific conversation."""
    return service.get_conversation_messages_with_sender(conversation_id, limit, offset)


@router.get("/{message_id}", response_model=MessageResponse)
def get_message(
    message_id: int,
    service: MessagesService = Depends(service_dependency)
):
    """Get a specific message by ID."""
    message = service.get_message(message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return MessageResponse.model_validate(message)


@router.put("/{message_id}", response_model=MessageResponse)
def update_message(
    message_id: int,
    update_data: MessageUpdate,
    user_id: int | None = None,  # For testing - should come from auth
    service: MessagesService = Depends(service_dependency)
):
    """Update a message (only by the sender)."""
    # TODO: Get current user ID from authentication context
    current_user_id = user_id or 1

    message = service.update_message(message_id, update_data, current_user_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found or access denied")
    return MessageResponse.model_validate(message)


@router.delete("/{message_id}", status_code=204)
def delete_message(
    message_id: int,
    user_id: int | None = None,  # For testing - should come from auth
    service: MessagesService = Depends(service_dependency)
):
    """Delete a message (soft delete, only by the sender)."""
    # TODO: Get current user ID from authentication context
    current_user_id = user_id or 1

    success = service.delete_message(message_id, current_user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found or access denied")


@router.get("/user/{user_id}", response_model=List[MessageResponse])
def get_user_messages(
    user_id: int,
    limit: int = Query(50, ge=1, le=100, description="Number of messages to return"),
    offset: int = Query(0, ge=0, description="Number of messages to skip"),
    service: MessagesService = Depends(service_dependency)
):
    """Get messages sent by a specific user."""
    messages = service.get_user_messages(user_id, limit, offset)
    return [MessageResponse.model_validate(msg) for msg in messages]


# Automatically mount sub-feature routers
auto_discover_routers(router, __file__, __package__)
