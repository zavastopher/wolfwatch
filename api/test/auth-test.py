from flask_jwt_extended import create_access_token
import pytest
from datetime import datetime
from unittest.mock import patch, Mock

from server import create_app
from models.models import Instructor
from extensions import db
from routes.auth import (
    make_pw_hash,
    make_salt,
    new_instructor,
    valid_email,
    valid_password,
    verify_password,
)


@pytest.fixture
def app():
    app = create_app(testing=True)
    app.config["TESTING"]
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "top secret"
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def init_db(app):
    with app.app_context():
        db.create_all()
        yield db  # this is where the testing happens :)
        db.drop_all()


@pytest.fixture
def patch_redis():
    with patch("extensions.jwt_redis_blocklist.get", return_value=None), \
         patch("extensions.jwt_redis_blocklist.set", return_value=None):
        yield


def test_login_user(client, init_db):
    # Add a test user to the database
    test_user = Instructor(
        email="test@test.com",
        userPassword=make_pw_hash("test@test.com", "testpassword", "testsalt"),
        passwordSalt="testsalt",
        firstName="Test",
        lastName="User",
        lastLogin=datetime.now(),
    )

    init_db.session.add(test_user)
    init_db.session.commit()

    # Test login with correct credentials
    response = client.post(
        "/auth/login", json={"email": "test@test.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert b"Logged in successfully" in response.data

    # Test login with incorrect credentials
    response = client.post(
        "/auth/login", json={"email": "test@test.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert b"Invalid email or password" in response.data


def test_user_registration(client, init_db):
    # Test registration with new email
    response = client.post(
        "/auth/register",
        data={
            "firstName": "New",
            "lastName": "User",
            "email": "newuser@ncsu.edu",
            "password": "newpassword",
            "confirmedPassword": "newpassword",
        },
    )
    assert response.status_code == 201
    assert b"User newuser@ncsu.edu created successfully" in response.data

    # Test registration with existing email
    response = client.post(
        "/auth/register",
        data={
            "firstName": "New",
            "lastName": "User",
            "email": "newuser@ncsu.edu",
            "password": "newpassword",
            "confirmedPassword": "newpassword",
        },
    )
    assert response.status_code == 400
    assert b"That email is already registered." in response.data


@patch("extensions.jwt_redis_blocklist.get", return_value=None)
@patch("extensions.jwt_redis_blocklist.set", return_value=None)
def test_logout(mock_set, mock_get, client, init_db):
    # Add a test user to the database
    test_user = Instructor(
        email="logouttest@test.com",
        userPassword=make_pw_hash("logouttest@test.com", "testpassword", "testsalt"),
        passwordSalt="testsalt",
        firstName="Logout",
        lastName="Test",
        lastLogin=datetime.now(),
    )
    init_db.session.add(test_user)
    init_db.session.commit()

    # Logout using the cookie
    response = client.delete(
        "/auth/logout",
        headers={"Authorization": f"Bearer {create_access_token(identity=test_user)}"},
    )
    assert response.status_code == 200
    assert b"signed out" in response.data

    assert f"logouttest@test.com signed out" in response.data.decode("utf-8")

    mock_set.assert_called_once()


def test_access_control(client, init_db, patch_redis):
    # Try to access protected route without token
    response = client.get("/auth/status")
    assert response.status_code == 401

    # Add a test user to the database
    test_user = Instructor(
        email="accesscontroltest@test.com",
        userPassword=make_pw_hash(
            "accesscontroltest@test.com", "testpassword", "testsalt"
        ),
        passwordSalt="testsalt",
        firstName="Access",
        lastName="Control",
        lastLogin=datetime.now(),
    )
    init_db.session.add(test_user)
    init_db.session.commit()

    # Try to access protected route with token
    response = client.get(
        "/auth/status",
        headers={"Authorization": f"Bearer {create_access_token(identity=test_user)}"},
    )
    assert response.status_code == 200


def test_new_instructor(init_db):
    email = "test@test.com"
    password = "testpassword"
    fname = "Test"
    lname = "User"
    instructor = new_instructor(email, password, fname, lname)
    assert instructor.email == email
    assert instructor.firstName == fname
    assert instructor.lastName == lname
    assert instructor.userPassword is not None
    assert instructor.passwordSalt is not None
    assert instructor.created is not None
    assert instructor.lastLogin is None


def test_make_salt():
    salt = make_salt()
    assert len(salt) == 120
    assert all(c.isalpha() for c in salt)


def test_make_pw_hash():
    email = "test@test.com"
    password = "testpassword"
    salt = make_salt()
    hashed_pw = make_pw_hash(email, password, salt)
    assert hashed_pw is not None
    assert len(hashed_pw) == 64  # Length of sha256 hash


def test_valid_email():
    assert not valid_email("test@test.com")
    assert not valid_email("invalidemail")
    assert not valid_email("invalid@.com")
    assert not valid_email("invalid@com")
    assert valid_email("instructor@ncsu.edu")


def test_valid_password():
    assert valid_password("password")
    assert not valid_password("short")


def test_verify_password():
    assert verify_password("password", "password")
    assert not verify_password("password", "different")
    assert not verify_password("password", "")


def test_make_pw_hash_no_salt():
    email = "test@test.com"
    password = "testpassword"
    hashed_pw = make_pw_hash(email, password)
    assert hashed_pw is not None
    # sha256 hash length
    assert len(hashed_pw) == 64


def test_valid_email_invalid_cases():
    assert not valid_email("invalidemail")
    assert not valid_email("invalid@.com")
    assert not valid_email("invalid@com")
    assert not valid_email("invalid@com.")
    assert not valid_email("invalid@.com.")
    assert not valid_email("invalid@com..")
    assert not valid_email("")


def test_valid_password_invalid_cases():
    assert not valid_password("short")
    assert not valid_password("")
    assert not valid_password("        ")


def test_verify_password_invalid_cases():
    assert not verify_password("password", "different")
    assert not verify_password("password", "")
    assert not verify_password("", "password")
    assert not verify_password("", "")
