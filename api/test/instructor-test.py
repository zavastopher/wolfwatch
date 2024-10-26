from datetime import datetime
from flask_jwt_extended import create_access_token
import pytest
from unittest.mock import patch

from server import create_app
from models.models import Instructor
from extensions import db
from routes.auth import make_pw_hash, make_salt


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
        yield db
        db.drop_all()


@pytest.fixture
def new_instructor_with_results():
    salt = make_salt()
    instructor = Instructor(
        firstName="Test",
        lastName="Man",
        email="test@testman.com",
        userPassword=make_pw_hash("test@testman.com", "testpassword", salt),
        passwordSalt=salt,
        created=datetime.utcnow(),
        lastLogin=None,
    )

    db.session.add(instructor)
    db.session.commit()

    db.session.commit()

    yield instructor

    db.session.delete(instructor)
    db.session.commit()


@pytest.fixture
def patch_redis():
    with patch("extensions.jwt_redis_blocklist.get", return_value=None), patch(
        "extensions.jwt_redis_blocklist.set", return_value=None
    ):
        yield


def test_get_instructor(client, init_db, new_instructor_with_results, patch_redis):
    headers = {
        "Authorization": f"Bearer {create_access_token(identity=new_instructor_with_results)}"
    }

    response = client.get("/instructor/", headers=headers)
    assert response.status_code == 200
    assert response.json["firstName"] == "Test"
    assert response.json["lastName"] == "Man"
    assert response.json["email"] == "test@testman.com"
    assert response.json["lastLogin"] is None


def test_get_instructor_invalid(
    client, init_db, new_instructor_with_results, patch_redis
):
    response = client.get("/instructor/")
    assert response.status_code == 401
    assert response.json["msg"] == "Missing Authorization Header"


def test_edit_instructor(client, init_db, new_instructor_with_results, patch_redis):
    headers = {
        "Authorization": f"Bearer {create_access_token(identity=new_instructor_with_results)}"
    }

    response = client.put(
        "/instructor/edit",
        json={"firstName": "New", "lastName": "Name", "email": "new@email.com"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json["firstName"] == "New"
    assert response.json["lastName"] == "Name"
    assert response.json["email"] == "new@email.com"

    response = client.get("/instructor/", headers=headers)
    assert response.status_code == 200
    assert response.json["firstName"] == "New"
    assert response.json["lastName"] == "Name"
    assert response.json["email"] == "new@email.com"
