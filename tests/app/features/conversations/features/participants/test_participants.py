"""
Tests for Participants feature.
"""
import pytest
from fastapi.testclient import TestClient


def test_participants_endpoint(client: TestClient):
    """Test that /participants endpoint is accessible."""
    response = client.get("/participants")
    assert response.status_code in [200, 404]  # Adjust based on your implementation


def test_participants_service():
    """Test ParticipantsService methods."""
    # TODO: Add service layer tests
    pass
