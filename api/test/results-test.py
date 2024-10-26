from datetime import datetime
from flask_jwt_extended import create_access_token
import pytest
from unittest.mock import patch

from server import create_app
from models.models import Assignment, Instructor, ScanResult
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
        firstName="test",
        lastName="test",
        email="test@test.com",
        userPassword=make_pw_hash("test@test.com", "testpassword", salt),
        passwordSalt=salt,
        created=datetime.utcnow(),
        lastLogin=None,
    )

    assignment = Assignment(
        assignmentId=1,
        instructorId=1,
        assignmentActive=True,
        dueDate=datetime.utcnow(),
        contents="test",
        courseName="test",
        title="test",
        lastNotificationCheck=datetime.utcnow(),
    )

    result = ScanResult(
        scanId=1,
        assignmentId=1,
        url="test.com",
        confidenceProbability=90.0,
    )
    # add instructor, assignment, and scan result to db

    db.session.add(instructor)
    db.session.commit()

    db.session.add(assignment)
    db.session.add(result)
    db.session.commit()

    yield instructor

    db.session.delete(instructor)
    db.session.delete(assignment)
    db.session.delete(result)
    db.session.commit()


@pytest.fixture
def patch_redis():
    with patch("extensions.jwt_redis_blocklist.get", return_value=None), patch(
        "extensions.jwt_redis_blocklist.set", return_value=None
    ):
        yield


def test_get_all_results(client, init_db, new_instructor_with_results, patch_redis):
    # Instructor should have 1 assignment and 1 scan result
    headers = {
        "Authorization": f"Bearer {create_access_token(identity=new_instructor_with_results)}"
    }

    response = client.get("/results/", headers=headers)
    json_data = response.get_json()
    assert response.status_code == 200
    assert len(json_data) == 1
    assert json_data[0]["scanId"] == 1
    assert json_data[0]["url"] == "test.com"
    assert json_data[0]["confidenceProbability"] == 90.0
    assert json_data[0]["assignment"]["assignmentId"] == 1
    assert json_data[0]["assignment"]["title"] == "test"


def test_get_result_by_id(client, init_db, new_instructor_with_results, patch_redis):
    headers = {
        "Authorization": f"Bearer {create_access_token(identity=new_instructor_with_results)}"
    }

    response = client.get("/results/1", headers=headers)
    json_data = response.get_json()
    assert response.status_code == 200
    assert len(json_data) == 4
    assert json_data["scanId"] == 1
    assert json_data["url"] == "test.com"
    assert json_data["confidenceProbability"] == 90.0
    assert json_data["assignment"]["assignmentId"] == 1
    assert json_data["assignment"]["title"] == "test"


def test_get_invalid_result_by_id(
    client, init_db, new_instructor_with_results, patch_redis
):
    headers = {
        "Authorization": f"Bearer {create_access_token(identity=new_instructor_with_results)}"
    }

    response = client.get("/results/2", headers=headers)
    assert response.status_code == 404


def test_get_unauthorized_result(
    client, init_db, new_instructor_with_results, patch_redis
):
    salt = make_salt()
    new_instructor = Instructor(
        firstName="test",
        lastName="test",
        email="test2@test.com",
        userPassword=make_pw_hash("test@test.com", "testpassword", salt),
        passwordSalt=salt,
        created=datetime.utcnow(),
        lastLogin=None,
    )

    db.session.add(new_instructor)
    db.session.commit()

    headers = {
        "Authorization": f"Bearer {create_access_token(identity=new_instructor)}"
    }

    response = client.get("/results/1", headers=headers)
    assert response.status_code == 401
