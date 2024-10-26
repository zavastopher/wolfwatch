from datetime import datetime
from flask_jwt_extended import create_access_token
import pytest
from unittest.mock import patch

from server import create_app
from models.models import Assignment, Instructor
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
def new_instructor():
    salt = make_salt()
    instructor = Instructor(
        firstName="test",
        lastName="test",
        email="test@test.com",
        userPassword=make_pw_hash("test@test.com", "testpassword", salt),
        passwordSalt=salt,
        created=datetime.utcnow(),
        lastLogin=None,
        frequencyId=3,
    )

    db.session.add(instructor)
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


@pytest.fixture
def mock_requests_post():
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        yield mock_post


@pytest.fixture
def mock_requests_delete():
    with patch("requests.delete") as mock_delete:
        mock_delete.return_value.status_code = 200
        yield mock_delete

@pytest.fixture
def mock_requests_post():
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        yield mock_post


def test_create_assignment(
    client, init_db, new_instructor, patch_redis, mock_requests_post
):
    headers = {
        "Authorization": f"Bearer {create_access_token(identity=new_instructor)}"
    }
    data = {
        "dueDate": "2029-11-11T12:00:00.000Z",
        "contents": "Test Assignment",
        "courseName": "Test Course",
        "title": "Test Title",
        "keyPhrases": ["phrase1", "phrase2"],
    }

    response = client.post("/assignments/", json=data, headers=headers)
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data["assignmentText"] == "Test Assignment"
    assert len(json_data["keyPhrases"]) == 2
    assert json_data["keyPhrases"][0] == "phrase1"
    assert json_data["keyPhrases"][1] == "phrase2"
    assert json_data["className"] == "Test Course"
    assert json_data["assignmentTitle"] == "Test Title"
    assert json_data["assignmentActive"] == True


def test_get_assignments(
    client, init_db, new_instructor, patch_redis, mock_requests_post
):
    # instructor should have no assignments
    headers = {
        "Authorization": f"Bearer {create_access_token(identity=new_instructor)}"
    }
    response = client.get("/assignments/", headers=headers)
    assert response.status_code == 200
    assert len(response.get_json()) == 0

    # retrieve assignment
    data = {
        "dueDate": "2029-11-11T12:00:00.000Z",
        "contents": "Test Assignment",
        "courseName": "Test Course",
        "title": "Test Title",
        "keyPhrases": ["phrase1", "phrase2"],
    }
    client.post("/assignments/", json=data, headers=headers)

    response = client.get("/assignments/", headers=headers)
    assert response.status_code == 200
    assert len(response.get_json()) == 1


def test_update_assignment(
    client, init_db, new_instructor, patch_redis, mock_requests_post, mock_requests_delete
):
    """
    Test updating an assignment. Initial assignment is active with
    some key phrases. Updated assignment is inactive with no key phrases.
    """
    headers = {
        "Authorization": f"Bearer {create_access_token(identity=new_instructor)}"
    }
    data = {
        "dueDate": "2029-11-11T12:00:00.000Z",
        "contents": "Test Assignment",
        "courseName": "Test Course",
        "title": "Test Title",
        "keyPhrases": ["phrase1", "phrase2"],
    }

    response = client.post("/assignments/", json=data, headers=headers)
    assert response.status_code == 201
    assert response.get_json()["assignmentActive"] == True
    assert response.get_json()["assignmentTitle"] == "Test Title"
    assert response.get_json()["assignmentText"] == "Test Assignment"
    assert response.get_json()["className"] == "Test Course"
    assert response.get_json()["keyPhrases"][0] == "phrase1"
    assert response.get_json()["keyPhrases"][1] == "phrase2"
    assignment_id = response.get_json()["assignmentId"]

    updated_data = {
        "dueDate": "2029-12-12T12:00:00.000Z",
        "contents": "Updated Assignment",
        "courseName": "Updated Course",
        "title": "Updated Title",
        "assignmentActive": False,
    }
    response = client.put(
        f"/assignments/{assignment_id}", json=updated_data, headers=headers
    )

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["assignmentActive"] == False
    assert json_data["assignmentTitle"] == "Updated Title"
    assert json_data["assignmentText"] == "Updated Assignment"
    assert json_data["className"] == "Updated Course"
    assert len(json_data["keyPhrases"]) == 0

    # add key phrases again
    updated_data = {
        "dueDate": "2029-12-12T12:00:00.000Z",
        "contents": "Updated Assignment",
        "courseName": "Updated Course",
        "title": "Updated Title",
        "assignmentActive": False,
        "keyPhrases": ["phrase3", "phrase4"],
    }

    response = client.put(
        f"/assignments/{assignment_id}", json=updated_data, headers=headers
    )

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["assignmentActive"] == False
    assert json_data["assignmentTitle"] == "Updated Title"
    assert json_data["assignmentText"] == "Updated Assignment"
    assert json_data["className"] == "Updated Course"
    assert len(json_data["keyPhrases"]) == 2


def test_delete_assignment(
    client,
    init_db,
    new_instructor,
    patch_redis,
    mock_requests_post,
    mock_requests_delete,
):
    headers = {
        "Authorization": f"Bearer {create_access_token(identity=new_instructor)}"
    }
    data = {
        "dueDate": "2029-11-11T12:00:00.000Z",
        "contents": "Test Assignment",
        "courseName": "Test Course",
        "title": "Test Title",
        "keyPhrases": ["phrase1", "phrase2"],
    }
    response = client.post("/assignments/", json=data, headers=headers)
    assignment_id = response.get_json()["assignmentId"]

    response = client.delete(f"/assignments/{assignment_id}", headers=headers)
    assert response.status_code == 200
    assert response.get_json()["msg"] == "Assignment deleted"

    response = client.get("/assignments/", headers=headers)
    assert response.status_code == 200
    assert len(response.get_json()) == 0
