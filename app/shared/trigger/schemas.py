"""
Shared schemas for trigger detection and management.
Reusable Pydantic models for trigger-related features.
"""
from pydantic import BaseModel
from typing import List, Optional


class TriggerInfoResponse(BaseModel):
    """Response schema for trigger info."""
    message: str
    capabilities: List[str]


class MentionAnalysisRequest(BaseModel):
    """Request schema for mention analysis."""
    content: str


class MentionAnalysisResponse(BaseModel):
    """Response schema for mention analysis."""
    mentions: List[str]
    has_mentions: bool


class TriggerEvaluationRequest(BaseModel):
    """Request schema for trigger evaluation."""
    content: str
    mentions: List[str]
    keywords: Optional[List[str]] = None
    patterns: Optional[List[str]] = None


class TriggerEvaluationResponse(BaseModel):
    """Response schema for trigger evaluation."""
    should_trigger: bool
    matched_keywords: List[str] = []
    matched_patterns: List[str] = []


# Example:
# class SharedExampleSchema(BaseModel):
#     id: int
#     name: str
