"""
Tests for Users feature.
"""
import pytest
from fastapi.testclient import TestClient
from app.shared.database.service import get_db
from app.features.users.service import UsersService
from app.features.users.schemas import UserCreate, UserUpdate


def test_users_endpoint(client: TestClient):
    """Test that /users endpoint is accessible."""
    response = client.get("/users/status")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    # Note: total_users is only included when database is connected
    if "database_connected" in data and data["database_connected"]:
        assert "total_users" in data


def test_users_service():
    """Test UsersService methods."""
    import time
    suffix = str(int(time.time()))  # Unique suffix for test isolation

    # Test with database session
    db = next(get_db())
    service = UsersService(db)

    # Test status
    status = service.status()
    assert "message" in status
    assert "database_connected" in status

    # Test creating a user
    user_data = UserCreate(
        email=f"test{suffix}@example.com",
        username=f"testuser{suffix}",
        full_name="Test User",
        password="securepassword123"
    )

    user = service.create_user(user_data)
    assert user.email == user_data.email
    assert user.username == user_data.username
    assert user.full_name == user_data.full_name
    assert user.is_active == True

    # Test getting user by ID
    retrieved_user = service.get_user_by_id(user.id)
    assert retrieved_user is not None
    assert retrieved_user.id == user.id

    # Test listing users
    users = service.list_users()
    assert len(users) >= 1
    assert any(u.id == user.id for u in users)

    # Test updating user
    update_data = UserUpdate(full_name="Updated Test User")
    updated_user = service.update_user(user.id, update_data)
    assert updated_user is not None
    assert updated_user.full_name == "Updated Test User"

    # Test deleting user
    assert service.delete_user(user.id) == True

    # Test getting deleted user returns None
    deleted_user = service.get_user_by_id(user.id)
    assert deleted_user is None

    db.close()


def test_user_crud_endpoints(client: TestClient):
    """Test full CRUD operations via API endpoints."""
    import time
    suffix = str(int(time.time()))

    # Create user
    user_data = {
        "email": f"api{suffix}@example.com",
        "username": f"apiuser{suffix}",
        "full_name": "API Test User",
        "password": "securepassword123"
    }

    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    created_user = response.json()

    # Get user by ID
    response = client.get(f"/users/{created_user['id']}")
    assert response.status_code == 200
    user = response.json()
    assert user["email"] == user_data["email"]

    # Update user
    update_data = {"full_name": "Updated API User"}
    response = client.put(f"/users/{created_user['id']}", json=update_data)
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["full_name"] == "Updated API User"

    # List users
    response = client.get("/users/")
    assert response.status_code == 200
    users_list = response.json()
    assert "users" in users_list
    assert "total" in users_list

    # Delete user
    response = client.delete(f"/users/{created_user['id']}")
    assert response.status_code == 204

    # Verify user is deleted
    response = client.get(f"/users/{created_user['id']}")
    assert response.status_code == 404


def test_user_validation(client: TestClient):
    """Test user input validation."""
    import time
    suffix = str(int(time.time()))

    # Create first user
    user_data = {
        "email": f"validation{suffix}@example.com",
        "username": f"validationuser{suffix}",
        "full_name": "Validation User",
        "password": "password123"
    }

    response = client.post("/users/", json=user_data)
    assert response.status_code == 201

    # Test duplicate email
    duplicate_email_data = {
        "email": f"validation{suffix}@example.com",  # Same email
        "username": f"differentuser{suffix}",
        "full_name": "Different User",
        "password": "password123"
    }

    response = client.post("/users/", json=duplicate_email_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

    # Test duplicate username
    duplicate_username_data = {
        "email": f"different{suffix}@example.com",
        "username": f"validationuser{suffix}",  # Same username
        "full_name": "Different User",
        "password": "password123"
    }

    response = client.post("/users/", json=duplicate_username_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_user_crud_endpoints(client: TestClient):
    """Test full CRUD operations via API endpoints."""
    import time
    suffix = str(int(time.time()))

    # Create user
    user_data = {
        "email": f"api{suffix}@example.com",
        "username": f"apiuser{suffix}",
        "full_name": "API Test User",
        "password": "securepassword123"
    }

    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    created_user = response.json()
    user_id = created_user["id"]
    assert created_user["email"] == user_data["email"]
    assert created_user["username"] == user_data["username"]

    # Get user by ID
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    retrieved_user = response.json()
    assert retrieved_user["id"] == user_id

    # List users
    response = client.get("/users/")
    assert response.status_code == 200
    users_list = response.json()
    assert "users" in users_list
    assert "total" in users_list
    assert users_list["total"] >= 1

    # Update user
    update_data = {"full_name": "Updated API User"}
    response = client.put(f"/users/{user_id}", json=update_data)
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["full_name"] == "Updated API User"

    # Delete user
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 204

    # Try to get deleted user
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 404

    # Try to delete again
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 404


def test_user_validation(client: TestClient):
    """Test user input validation."""
    import time
    suffix = str(int(time.time()))

    # Create first user
    user_data = {
        "email": f"validation{suffix}@example.com",
        "username": f"validationuser{suffix}",
        "full_name": "Validation User",
        "password": "password123"
    }

    # Create first user
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201

    # Try to create duplicate
    user_data["username"] = "user2"
    response = client.post("/users/", json=user_data)
    assert response.status_code == 400

    # Test duplicate username
    user_data["email"] = "different@example.com"
    user_data["username"] = f"validationuser{suffix}"  # Same username as first user
    response = client.post("/users/", json=user_data)
    assert response.status_code == 400

    # Test invalid email
    user_data["email"] = "invalid-email"
    user_data["username"] = "user3"
    response = client.post("/users/", json=user_data)
    assert response.status_code == 422  # Validation error

    # Test short password
    user_data["email"] = "valid@example.com"
    user_data["password"] = "short"
    response = client.post("/users/", json=user_data)
    assert response.status_code == 422
