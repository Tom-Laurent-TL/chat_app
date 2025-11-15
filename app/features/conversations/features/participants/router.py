from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.shared.database.service import get_db
from app.shared.routing import auto_discover_routers
from .service import ParticipantsService
from app.features.conversations.schemas import ConversationParticipantResponse

router = APIRouter(prefix="/participants", tags=["participants"])


def get_participants_service(db: Session = Depends(get_db)) -> ParticipantsService:
    """Dependency to get participants service with database session."""
    return ParticipantsService(db)


@router.get("/", response_model=List[ConversationParticipantResponse])
def get_participants(
    conversation_id: int,
    service: ParticipantsService = Depends(get_participants_service)
):
    """Get all participants for a conversation."""
    participants = service.get_participants(conversation_id)
    return participants


@router.post("/", status_code=201)
def add_participant(
    conversation_id: int,
    user_id: int,
    role: str = "participant",
    service: ParticipantsService = Depends(get_participants_service)
):
    """Add a participant to a conversation."""
    if not service.add_participant(conversation_id, user_id, role):
        raise HTTPException(
            status_code=400,
            detail="Could not add participant (conversation not found or user already participant)"
        )

    return {"message": "Participant added successfully"}


@router.post("/bots", status_code=201)
def add_bot_participant(
    conversation_id: int,
    bot_id: int,
    role: str = "bot",
    service: ParticipantsService = Depends(get_participants_service)
):
    """Add a bot as a participant to a conversation."""
    if not service.add_bot_participant(conversation_id, bot_id, role):
        raise HTTPException(
            status_code=400,
            detail="Could not add bot participant (conversation not found or bot already participant)"
        )

    return {"message": "Bot participant added successfully"}


@router.delete("/bots/{bot_id}", status_code=204)
def remove_bot_participant(
    conversation_id: int,
    bot_id: int,
    service: ParticipantsService = Depends(get_participants_service)
):
    """Remove a bot participant from a conversation."""
    if not service.remove_bot_participant(conversation_id, bot_id):
        raise HTTPException(
            status_code=404,
            detail=f"Bot participant not found in conversation {conversation_id}"
        )


@router.get("/status")
def get_status(service: ParticipantsService = Depends(get_participants_service)):
    """Get status of the participants feature."""
    return service.status()


# Automatically mount sub-feature routers
auto_discover_routers(router, __file__, __package__)
