import os
from datetime import datetime, timezone, timedelta

# Flask migrate is included for future functionality in automating database updates
from flask_migrate import Migrate
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    get_jwt_identity,
    set_access_cookies,
)

from config import *
from extensions import db, jwt, logger, mail
from routes import register_blueprints


def create_app(testing=False):
    app = Flask(__name__)

    if testing:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    else:
        configure_app(app)
        mail.init_app(app)

    migrate = Migrate(app, db)
    db.init_app(app)
    jwt.init_app(app)
    app.logger.handlers = logger.handlers
    app.logger.setLevel(logger.level)
    CORS(app, supports_credentials=True)
    register_blueprints(app)
    register_callbacks(app)

    return app


def configure_app(app):
    app.config["DEBUG"] = DEBUG
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=TOKEN_EXPIRATION)
    app.config["JWT_COOKIE_SECURE"] = COOKIE_SECURE
    app.config["JWT_TOKEN_LOCATION"] = TOKEN_LOCATION
    app.config["JWT_SESSION_COOKIE"] = SESSION_COOKIE
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = TRACK_MODIFICATIONS
    app.config["MAIL_SERVER"] = MAIL_SERVER
    app.config["MAIL_PORT"] = MAIL_PORT
    app.config["MAIL_USE_SSL"] = MAIL_USE_SSL
    app.config["MAIL_USE_TLS"] = MAIL_USE_TLS
    app.config["MAIL_DEBUG"] = MAIL_DEBUG
    app.config["MAIL_USERNAME"] = MAIL_USERNAME
    app.config["MAIL_PASSWORD"] = MAIL_PASSWORD
    app.config["MAIL_DEFAULT_SENDER"] = MAIL_DEFAULT_SENDER

def register_callbacks(app):
    @app.after_request
    def refresh_expiring_jwts(response):
        """
        At the end of every request, check if access token expires within the next 30 minutes.
        If so, set a new JWT cookie and return it as part of the response.

        Exceptions:
        - If there's no valid JWT or any other issues arise while attempting to refresh the token,
        the original response is returned without modification.
        """
        try:
            exp_timestamp = get_jwt()["exp"]
            now = datetime.now(timezone.utc)
            target_timestamp = (now + timedelta(minutes=30)).timestamp()

            if target_timestamp > exp_timestamp:
                access_token = create_access_token(identity=get_jwt_identity())
                set_access_cookies(response, access_token, max_age=COOKIE_EXPIRATION)
            return response
        except (RuntimeError, KeyError):
            # Case where there is not a valid JWT. Just return the original response
            return response


if __name__ == "__main__":
    app = create_app()
    migrate = Migrate(app, db)
    app.run(debug=app.config["DEBUG"], host=HOST, port=PORT)
