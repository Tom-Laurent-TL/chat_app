from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.shared.database.service import get_db
from app.shared.routing import auto_discover_routers
from .service import ConversationsService
from .schemas import (
    ConversationCreate, ConversationUpdate, ConversationResponse, ConversationListResponse, ConversationsStatusResponse
)

router = APIRouter(
    prefix="/conversations",
    tags=["conversations"],
    dependencies=[Depends(get_db)]
)


@router.get("/status", response_model=ConversationsStatusResponse)
def get_status(db: Session = Depends(get_db)):
    """Get status of the conversations feature."""
    service = ConversationsService(db)
    return service.status()


@router.post("/", response_model=ConversationResponse, status_code=201)
def create_conversation(
    conversation_data: ConversationCreate,
    created_by_id: int | None = None,  # For testing - should come from auth
    db: Session = Depends(get_db)
):
    """Create a new conversation."""
    # TODO: Get current user ID from authentication context
    # For now, we'll use a placeholder user ID or the provided one for testing
    user_id = created_by_id or 1

    service = ConversationsService(db)
    conversation = service.create_conversation(conversation_data, user_id)

    # Get participants data
    from app.features.conversations.features.participants.service import ParticipantsService
    participants_service = ParticipantsService(db)
    participants_data = participants_service.get_participants(conversation.id)  # type: ignore

    # Create response with participants
    response_data = {
        "id": conversation.id,
        "title": conversation.title,
        "description": conversation.description,
        "created_by_id": conversation.created_by_id,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "is_active": conversation.is_active,
        "participants": participants_data
    }

    return ConversationResponse(**response_data)


@router.get("/", response_model=ConversationListResponse)
def list_conversations(
    skip: int = Query(0, ge=0, description="Number of conversations to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of conversations to return"),
    user_id: int | None = Query(None, ge=1, description="Filter by user ID who created the conversations"),
    db: Session = Depends(get_db)
):
    """List conversations with pagination. Optionally filter by user_id."""
    service = ConversationsService(db)
    conversations = service.list_conversations(skip=skip, limit=limit, user_id=user_id)
    total = service.get_total_conversations(user_id=user_id)

    # Convert conversations to response format with participants
    from app.features.conversations.features.participants.service import ParticipantsService
    participants_service = ParticipantsService(db)
    conversation_responses = []
    for conversation in conversations:
        participants_data = participants_service.get_participants(conversation.id)  # type: ignore
        response_data = {
            "id": conversation.id,
            "title": conversation.title,
            "description": conversation.description,
            "created_by_id": conversation.created_by_id,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
            "is_active": conversation.is_active,
            "participants": participants_data
        }
        conversation_responses.append(ConversationResponse(**response_data))

    return ConversationListResponse(
        conversations=conversation_responses,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Get a conversation by ID."""
    service = ConversationsService(db)
    conversation = service.get_conversation_by_id(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail=f"Conversation with id {conversation_id} not found")

    # Get participants data
    from app.features.conversations.features.participants.service import ParticipantsService
    participants_service = ParticipantsService(db)
    participants_data = participants_service.get_participants(conversation.id)  # type: ignore

    # Create response with participants
    response_data = {
        "id": conversation.id,
        "title": conversation.title,
        "description": conversation.description,
        "created_by_id": conversation.created_by_id,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "is_active": conversation.is_active,
        "participants": participants_data
    }

    return ConversationResponse(**response_data)


@router.put("/{conversation_id}", response_model=ConversationResponse)
def update_conversation(
    conversation_id: int,
    conversation_data: ConversationUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing conversation."""
    service = ConversationsService(db)
    conversation = service.update_conversation(conversation_id, conversation_data)
    if not conversation:
        raise HTTPException(status_code=404, detail=f"Conversation with id {conversation_id} not found")

    # Get participants data
    from app.features.conversations.features.participants.service import ParticipantsService
    participants_service = ParticipantsService(db)
    participants_data = participants_service.get_participants(conversation.id)  # type: ignore

    # Create response with participants
    response_data = {
        "id": conversation.id,
        "title": conversation.title,
        "description": conversation.description,
        "created_by_id": conversation.created_by_id,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "is_active": conversation.is_active,
        "participants": participants_data
    }

    return ConversationResponse(**response_data)


@router.delete("/{conversation_id}", status_code=204)
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Delete a conversation (soft delete)."""
    service = ConversationsService(db)
    if not service.delete_conversation(conversation_id):
        raise HTTPException(status_code=404, detail=f"Conversation with id {conversation_id} not found")


# Automatically mount sub-feature routers
auto_discover_routers(router, __file__, __package__)
