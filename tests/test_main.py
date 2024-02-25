# This file contains tests for the main routes of the application
from app.models import User
from app.security import hash_password


def test_register_user_success(client):
    response = client.post("/register", json={
        "username": "testuser",
        "password": "securepassword",
        "full_name": "Test User",
    })
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"


def test_register_user_existing_username(client, session):
    user = User(
        username="anotheruser",
        password="anotherpassword",
        full_name="Another User",
    )
    session.add(user)

    response = client.post("/register", json={
        "username": "anotheruser",
        "password": "anotherpassword",
        "full_name": "Another User",
    })

    assert response.status_code == 400
    expected_response = {
        "detail": "User with the same username already exists"
    }
    assert response.json() == expected_response


def test_login_success(client, session):
    password = "securepassword"
    hashed_password = hash_password(password)
    user = User(
        username="testuser",
        password=hashed_password,
        full_name="Test User",
    )
    session.add(user)

    response = client.post("/login", data={
        "username": "testuser",
        "password": password,
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_incorrect_credentials(client):
    response = client.post("/login", data={
        "username": "nonexistentuser",
        "password": "wrongpassword",
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_read_users_me_authenticated(client, session, valid_auth_header):
    user = User(
        username="testuser",
        password="securepassword",
        full_name="Test User",
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    response = client.get(
        "users/me/",
        headers=valid_auth_header,
    )
    assert response.status_code == 200
    json_dict = response.json()
    assert json_dict["username"] == "testuser"
    assert json_dict["full_name"] == "Test User"
    assert json_dict["id"] == user.id


def test_read_users_me_not_authenticated(client):
    response = client.get("/users/me/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
