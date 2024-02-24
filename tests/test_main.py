from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_register_user():
    # Test case for registering a new user
    user_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == 201
    assert response.json() == {
        "email": "test@example.com"
    }

    # Test case for registering a user with an existing email
    response = client.post("/register", json=user_data)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "User with the same email already exists"
    }
