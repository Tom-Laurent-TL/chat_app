"""
Tests for Conversations feature.
"""
import pytest
import time
from fastapi.testclient import TestClient
from app.shared.database.service import get_db
from app.features.conversations.service import ConversationsService
from app.features.conversations.features.participants.service import ParticipantsService
from app.features.conversations.schemas import ConversationCreate, ConversationUpdate
from app.features.users.service import UsersService
from app.features.users.schemas import UserCreate


def test_conversations_endpoint(client: TestClient):
    """Test that conversations endpoints are accessible."""
    # Test status endpoint
    response = client.get("/conversations/status")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_conversations_service():
    """Test ConversationsService methods."""
    db = next(get_db())
    service = ConversationsService(db)

    # Test status
    status = service.status()
    assert "message" in status

    # Test get_total_conversations (should be 0 initially)
    total = service.get_total_conversations()
    assert total == 0


def test_conversation_crud_operations():
    """Test full CRUD operations for conversations."""
    import time
    suffix = str(int(time.time()))  # Unique suffix for test isolation

    db = next(get_db())
    service = ConversationsService(db)
    user_service = UsersService(db)

    # Create a test user first
    user_data = UserCreate(
        email=f"test{suffix}@example.com",
        username=f"testuser{suffix}",
        full_name="Test User",
        password="securepassword123"
    )
    test_user = user_service.create_user(user_data)

    # Create a conversation
    conversation_data = ConversationCreate(
        title="Test Conversation",
        description="A test conversation for unit testing"
    )
    conversation = service.create_conversation(conversation_data, test_user.id)

    assert conversation.title == "Test Conversation"
    assert conversation.description == "A test conversation for unit testing"
    assert conversation.created_by_id == test_user.id
    assert conversation.is_active == True

    # Get the conversation by ID
    retrieved = service.get_conversation_by_id(conversation.id)
    assert retrieved is not None
    assert retrieved.id == conversation.id
    assert retrieved.title == "Test Conversation"

    # Update the conversation
    update_data = ConversationUpdate(
        title="Updated Test Conversation",
        description="Updated description"
    )
    updated = service.update_conversation(conversation.id, update_data)
    assert updated is not None
    assert updated.title == "Updated Test Conversation"
    assert updated.description == "Updated description"

    # List conversations
    conversations = service.list_conversations()
    assert len(conversations) == 1
    assert conversations[0].id == conversation.id

    # Check total count
    total = service.get_total_conversations()
    assert total == 1

    # Delete the conversation (soft delete)
    deleted = service.delete_conversation(conversation.id)
    assert deleted == True

    # Verify it's soft deleted
    retrieved_after_delete = service.get_conversation_by_id(conversation.id)
    assert retrieved_after_delete is None

    # Verify total count is now 0
    total_after_delete = service.get_total_conversations()
    assert total_after_delete == 0


def test_conversation_user_filtering():
    """Test filtering conversations by user."""
    import time
    suffix = str(int(time.time()))  # Unique suffix for test isolation

    db = next(get_db())
    service = ConversationsService(db)
    user_service = UsersService(db)

    # Create two test users
    user1_data = UserCreate(
        email=f"user1{suffix}@example.com",
        username=f"user1{suffix}",
        full_name="User One",
        password="securepassword123"
    )
    user2_data = UserCreate(
        email=f"user2{suffix}@example.com",
        username=f"user2{suffix}",
        full_name="User Two",
        password="securepassword123"
    )
    user1 = user_service.create_user(user1_data)
    user2 = user_service.create_user(user2_data)

    # Create conversations for user1
    conv1_data = ConversationCreate(title="User1 Conversation 1")
    conv2_data = ConversationCreate(title="User1 Conversation 2")
    conv1 = service.create_conversation(conv1_data, user1.id)
    conv2 = service.create_conversation(conv2_data, user1.id)

    # Create conversation for user2
    conv3_data = ConversationCreate(title="User2 Conversation")
    conv3 = service.create_conversation(conv3_data, user2.id)

    # Test filtering by user1
    user1_conversations = service.list_conversations(user_id=user1.id)
    assert len(user1_conversations) == 2
    assert all(conv.created_by_id == user1.id for conv in user1_conversations)
    assert {conv.title for conv in user1_conversations} == {"User1 Conversation 1", "User1 Conversation 2"}

    # Test filtering by user2
    user2_conversations = service.list_conversations(user_id=user2.id)
    assert len(user2_conversations) == 1
    assert user2_conversations[0].created_by_id == user2.id
    assert user2_conversations[0].title == "User2 Conversation"

    # Test total counts by user
    user1_total = service.get_total_conversations(user_id=user1.id)
    user2_total = service.get_total_conversations(user_id=user2.id)
    assert user1_total == 2
    assert user2_total == 1

    # Test no filter (all conversations)
    all_conversations = service.list_conversations()
    all_total = service.get_total_conversations()
    assert len(all_conversations) == 3
    assert all_total == 3

    # Clean up
    service.delete_conversation(conv1.id)
    service.delete_conversation(conv2.id)
    service.delete_conversation(conv3.id)


def test_conversation_participants():
    """Test conversation participant management."""
    import time
    suffix = str(int(time.time()))  # Unique suffix for test isolation

    db = next(get_db())
    service = ConversationsService(db)
    participants_service = ParticipantsService(db)
    user_service = UsersService(db)

    # Create test users
    user1_data = UserCreate(
        email=f"participant1{suffix}@example.com",
        username=f"participant1{suffix}",
        full_name="Participant One",
        password="securepassword123"
    )
    user2_data = UserCreate(
        email=f"participant2{suffix}@example.com",
        username=f"participant2{suffix}",
        full_name="Participant Two",
        password="securepassword123"
    )
    user1 = user_service.create_user(user1_data)
    user2 = user_service.create_user(user2_data)

    # Create a conversation
    conv_data = ConversationCreate(
        title="Participant Test Conversation",
        description="A test conversation for participant management"
    )
    conversation = service.create_conversation(conv_data, user1.id)

    # The creator should automatically be added as a participant with 'owner' role
    participants = participants_service.get_participants(conversation.id)
    assert len(participants) == 1
    assert participants[0]['id'] == user1.id
    assert participants[0]['role'] == 'owner'

    # Add user2 as a participant
    success = participants_service.add_participant(conversation.id, user2.id, 'participant')
    assert success == True

    # Check participants again
    participants = participants_service.get_participants(conversation.id)
    assert len(participants) == 2
    participant_ids = {p['id'] for p in participants}
    assert participant_ids == {user1.id, user2.id}

    # Check roles
    roles = {p['id']: p['role'] for p in participants}
    assert roles[user1.id] == 'owner'
    assert roles[user2.id] == 'participant'

    # Try to add the same user again (should fail)
    success = participants_service.add_participant(conversation.id, user2.id)
    assert success == False

    # Check if user is participant
    assert participants_service.is_participant(conversation.id, user1.id) == True
    assert participants_service.is_participant(conversation.id, user2.id) == True
    assert participants_service.is_participant(conversation.id, 999) == False  # Non-existent user

    # Remove user2 from conversation
    success = participants_service.remove_participant(conversation.id, user2.id)
    assert success == True

    # Check participants after removal
    participants = participants_service.get_participants(conversation.id)
    assert len(participants) == 1
    assert participants[0]['id'] == user1.id

    # Try to remove the same user again (should fail)
    success = participants_service.remove_participant(conversation.id, user2.id)
    assert success == False

    # Clean up
    service.delete_conversation(conversation.id)


def test_conversation_validation():
    """Test conversation data validation."""
    import time
    suffix = str(int(time.time()))  # Unique suffix for test isolation

    db = next(get_db())
    service = ConversationsService(db)
    user_service = UsersService(db)

    # Create a test user first
    user_data = UserCreate(
        email=f"minimal{suffix}@example.com",
        username=f"minimaluser{suffix}",
        full_name="Minimal User",
        password="securepassword123"
    )
    test_user = user_service.create_user(user_data)

    # Test creating conversation with minimal data
    minimal_data = ConversationCreate(title="Minimal")
    conversation = service.create_conversation(minimal_data, test_user.id)
    assert conversation.title == "Minimal"
    assert conversation.description is None

    # Test updating with partial data
    update_data = ConversationUpdate(title="Updated Title")
    updated = service.update_conversation(conversation.id, update_data)
    assert updated.title == "Updated Title"
    assert updated.description is None  # Should remain unchanged

    # Clean up
    service.delete_conversation(conversation.id)


def test_conversation_crud_endpoints(client: TestClient):
    """Test conversation CRUD endpoints via API."""
    import time
    suffix = str(int(time.time()))  # Unique suffix for test isolation

    # First create a user to be the conversation creator
    user_response = client.post("/users/", json={
        "email": f"conv_test{suffix}@example.com",
        "username": f"conv_user{suffix}",
        "full_name": "Conversation Test User",
        "password": "securepassword123"
    })
    assert user_response.status_code == 201
    user_data = user_response.json()

    # Create a conversation
    conversation_data = {
        "title": "API Test Conversation",
        "description": "Testing conversation creation via API"
    }
    create_response = client.post("/conversations/", json=conversation_data)
    assert create_response.status_code == 201
    conversation = create_response.json()
    assert conversation["title"] == "API Test Conversation"
    assert conversation["description"] == "Testing conversation creation via API"
    assert "id" in conversation
    assert "created_at" in conversation

    conversation_id = conversation["id"]

    # Get the conversation by ID
    get_response = client.get(f"/conversations/{conversation_id}")
    assert get_response.status_code == 200
    retrieved = get_response.json()
    assert retrieved["id"] == conversation_id
    assert retrieved["title"] == "API Test Conversation"

    # Update the conversation
    update_data = {
        "title": "Updated API Test Conversation",
        "description": "Updated via API"
    }
    update_response = client.put(f"/conversations/{conversation_id}", json=update_data)
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["title"] == "Updated API Test Conversation"
    assert updated["description"] == "Updated via API"

    # List conversations
    list_response = client.get("/conversations/")
    assert list_response.status_code == 200
    conversations_list = list_response.json()
    assert "conversations" in conversations_list
    assert "total" in conversations_list
    assert conversations_list["total"] >= 1
    assert len(conversations_list["conversations"]) >= 1

    # Delete the conversation
    delete_response = client.delete(f"/conversations/{conversation_id}")
    assert delete_response.status_code == 204

    # Verify it's deleted (should return 404)
    get_after_delete = client.get(f"/conversations/{conversation_id}")
    assert get_after_delete.status_code == 404


def test_conversation_user_filtering_endpoints(client: TestClient):
    """Test conversation user filtering via API endpoints."""
    import time
    suffix = str(int(time.time()))  # Unique suffix for test isolation

    # Create two users
    user1_response = client.post("/users/", json={
        "email": f"user1_api{suffix}@example.com",
        "username": f"user1_api{suffix}",
        "full_name": "User One API",
        "password": "securepassword123"
    })
    assert user1_response.status_code == 201
    user1_data = user1_response.json()

    user2_response = client.post("/users/", json={
        "email": f"user2_api{suffix}@example.com",
        "username": f"user2_api{suffix}",
        "full_name": "User Two API",
        "password": "securepassword123"
    })
    assert user2_response.status_code == 201
    user2_data = user2_response.json()

    # Create conversations for user1
    conv1_response = client.post("/conversations/", json={
        "title": "User1 API Conversation 1",
        "description": "First conversation for user1"
    }, params={"created_by_id": user1_data["id"]})
    assert conv1_response.status_code == 201
    conv1_data = conv1_response.json()

    conv2_response = client.post("/conversations/", json={
        "title": "User1 API Conversation 2",
        "description": "Second conversation for user1"
    }, params={"created_by_id": user1_data["id"]})
    assert conv2_response.status_code == 201
    conv2_data = conv2_response.json()

    # Create conversation for user2
    conv3_response = client.post("/conversations/", json={
        "title": "User2 API Conversation",
        "description": "Conversation for user2"
    }, params={"created_by_id": user2_data["id"]})
    assert conv3_response.status_code == 201
    conv3_data = conv3_response.json()

    # Test filtering by user1
    user1_list_response = client.get(f"/conversations/?user_id={user1_data['id']}")
    assert user1_list_response.status_code == 200
    user1_list = user1_list_response.json()
    assert user1_list["total"] == 2
    assert len(user1_list["conversations"]) == 2
    assert all(conv["created_by_id"] == user1_data["id"] for conv in user1_list["conversations"])

    # Test filtering by user2
    user2_list_response = client.get(f"/conversations/?user_id={user2_data['id']}")
    assert user2_list_response.status_code == 200
    user2_list = user2_list_response.json()
    assert user2_list["total"] == 1
    assert len(user2_list["conversations"]) == 1
    assert user2_list["conversations"][0]["created_by_id"] == user2_data["id"]
    assert user2_list["conversations"][0]["title"] == "User2 API Conversation"

    # Test no filter (all conversations)
    all_list_response = client.get("/conversations/")
    assert all_list_response.status_code == 200
    all_list = all_list_response.json()
    assert all_list["total"] >= 3  # At least the 3 we created
    assert len(all_list["conversations"]) >= 3

    # Clean up - delete conversations
    client.delete(f"/conversations/{conv1_data['id']}")
    client.delete(f"/conversations/{conv2_data['id']}")
    client.delete(f"/conversations/{conv3_data['id']}")
