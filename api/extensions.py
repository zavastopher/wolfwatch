"""
extensions.py

Purpose:
This file centralizes the instantiation of extensions, modules, and configurations that are widely used throughout WolfWatch's Flask application. By defining these extensions outside of the app context, the file prevents circular imports and simplifies the app structure by offering directory-level access to shared resources.

==Contents==

Database Extensions:
    - `db`: Represents the Flask-SQLAlchemy extension instance. It provides ORM functionalities for SQL databases.
    
Authentication & Authorization:
    - `jwt`: Represents the Flask-JWT-Extended extension instance. It facilitates the creation, verification, and management of JSON Web Tokens.
    - `jwt_redis_blocklist`: An instance of Redis which is configured to store JWTs that are blocklisted, ensuring they cannot be used for further authentication.

Emailing:
    - `mail`: An instance of a flask-mailing object capable of programmatically sending emails
    - `redis_pw_reset_token_store`: Instance of Redis configured to store valid password reset tokens

Logging:
    - `logger`: A logging instance configured to capture application-level logs. It uses a rotating file handler to ensure logs are stored efficiently and are easily manageable.
"""
import os
import redis
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import logging
from logging.handlers import RotatingFileHandler
from flask_mailing import Mail

from config import REDIS_HOST, REDIS_PORT, REDIS_BLOCKLIST_DB

# Database initialization
db = SQLAlchemy()

# Authentication & Authorization initialization
jwt = JWTManager()
jwt_redis_blocklist = redis.StrictRedis(
    host=REDIS_HOST, port=REDIS_PORT, db=REDIS_BLOCKLIST_DB, decode_responses=True
)

# Mail initialization
mail = Mail()
redis_pw_reset_token_store = redis.StrictRedis(
    host=REDIS_HOST, port=REDIS_PORT, db=2, decode_responses=True
)

# Logger initialization
logger = logging.getLogger(__name__)
if not os.path.exists("log"):
    os.mkdir("log")
logger = logging.getLogger(__name__)
handler = RotatingFileHandler("log/flask_output.log", maxBytes=10000, backupCount=1)
formatter = logging.Formatter(
    "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s"
)
handler.setFormatter(formatter)
logger.setLevel(logging.INFO)
logger.addHandler(handler)
