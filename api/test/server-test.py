import pytest
from flask import Flask
from server import create_app


@pytest.fixture
def app():
    app = create_app(testing=True)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_create_app(app):
    assert isinstance(app, Flask)


def test_configure_app(app):
    assert "JWT_ACCESS_TOKEN_EXPIRES" in app.config
    assert "JWT_COOKIE_SECURE" in app.config
    assert "JWT_TOKEN_LOCATION" in app.config
    assert "JWT_SESSION_COOKIE" in app.config
    assert "SQLALCHEMY_DATABASE_URI" in app.config
    assert "SQLALCHEMY_TRACK_MODIFICATIONS" in app.config


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 404
