from app.models import User
from app.security import hash_password
from app.utils import DictToObject
from tests.test_data import sample_parser_response_success


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


def test_subscribe_to_feed(client, session, valid_auth_header, mocker):
    mocked_parser = mocker.patch(
        "main.feedparser.parse",
        return_value=DictToObject(sample_parser_response_success),
    )

    user = User(
        username="testuser",
        password="securepassword",
        full_name="Test User",
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    test_url = "https://example.com/rss-feed"
    response = client.post(
        "/feed/subscribe",
        headers=valid_auth_header,
        json={"feed_url": test_url},
    )
    assert response.status_code == 201
    assert response.json()["feed_url"] == test_url
    assert user.subscribed_feeds[0].feed.feed_url == test_url

    mocked_parser.assert_called_once_with(test_url)
