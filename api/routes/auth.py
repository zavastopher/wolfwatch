from datetime import datetime
import hashlib
import random
import string
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    set_access_cookies,
    get_jwt,
    current_user,
)
import re

from extensions import jwt_redis_blocklist, db, jwt, logger
from models.models import Instructor, Frequency
from config import COOKIE_EXPIRATION, TOKEN_EXPIRATION

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["POST"])
def login_user():
    """
    Logs in a user with the provided email and password.

    Returns:
        A JSON response with a message indicating successful login or an error message if login fails.
    """
    email = request.json.get("email")
    password = request.json.get("password")

    try:
        instructor = Instructor.query.filter_by(email=email.lower()).one_or_none()
    except Exception as e:
        logger.error(f"Error logging in for user {email}. Exception: {e}")
        return jsonify({"msg": "Error logging in"}), 400

    # instructor does not exist
    if not instructor:
        return jsonify({"msg": "Invalid email or password"}), 401

    # incorrect password
    salt, hash_password = instructor.passwordSalt, instructor.userPassword
    if not make_pw_hash(email, password, salt) == hash_password:
        return jsonify({"msg": "Invalid email or password"}), 401

    instructor.lastLogin = datetime.now()
    db.session.commit()

    # create access token for the user with max age of 1 hour
    access_token = create_access_token(identity=instructor)
    response = jsonify(
        {
            "msg": "Logged in successfully",
            "firstName": instructor.firstName,
            "lastName": instructor.lastName,
        }
    )
    set_access_cookies(response, access_token, max_age=COOKIE_EXPIRATION)
    logger.info("User logged in: %s", email)

    return response


@auth.route("/register", methods=["POST"])
def register():
    """
    Registers a new instructor with the provided information.

    Returns:
        A JSON response containing a success message if the registration is successful,
        or an error message if there was an issue with the provided information.
    """
    fname = request.form.get("firstName")
    lname = request.form.get("lastName")
    email = request.form.get("email")
    password = request.form.get("password")
    confirmed_password = request.form.get("confirmedPassword")
    try:
        instructor = Instructor.query.filter_by(email=email.lower()).first()
    except Exception as e:
        logger.error("Error registering user: %s", e)
        return jsonify({"msg": "error registering user"}), 400
    if instructor:
        error = "That email is already registered."
        logger.warning("Registration for %s failed: %s", email, error)
        return jsonify({"msg": error}), 400
    if not valid_email(email):
        error = "Invalid Email Address"
        logger.warning("Registration for %s failed: %s", email, error)
        return jsonify({"msg": error}), 400
    if not valid_password(password):
        error = "Please Make Your Password at least 6 characters long"
        logger.warning("Registration for %s failed: %s", email, error)
        return jsonify({"msg": error}), 400
    if not verify_password(password, confirmed_password):
        error = "Passwords do not match"
        logger.warning("Registration for %s failed: %s", email, error)
        return jsonify({"msg": error}), 400

    try:
        new_instructor(email, password, fname, lname)
    except Exception as e:
        logger.error("Error creating new instructor: %s", e)
        return jsonify({"msg": str(e)}), 400

    logger.info("New user registered: %s", email)
    return jsonify({"msg": f"User {email} created successfully"}), 201


@auth.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    """
    Logout the user by revoking their JWT token until it expires, rendering it useless.

    Returns:
        A JSON response indicating that the token has been successfully revoked.
    """
    token = get_jwt()
    jti = token["jti"]

    jwt_redis_blocklist.set(jti, "", ex=TOKEN_EXPIRATION)

    logger.info("User signed out: %s", current_user.email)
    return jsonify({"msg": f"{current_user.email} signed out"}), 200


@auth.route("/status", methods=["GET"])
@jwt_required()
def get_status():
    """
    Endpoint used to check authentication status.

    Returns:
        Response will only be returned if the user is actively authenticated.
    """
    return jsonify(current_user.as_dict())


@jwt.user_identity_loader
def user_identity_lookup(instructor):
    """
    Callback function that takes instructor object passed into
    JWT and converts it to a JSON serializable format.

    Args:
        instructor (object): An instructor object.

    Returns:
        int: The ID of the instructor.
    """
    if isinstance(instructor, Instructor):
        return instructor.instructorId
    return instructor


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    """
    Callback function that loads the instructor from the database
    when a protected endpoint is accessed.


    Args:
        _jwt_header (dict): The JWT header.
        jwt_data (dict): The JWT data.

    Returns:
        Instructor: The instructor object or None if the lookup fails.
    """
    identity = jwt_data["sub"]
    return Instructor.query.filter_by(instructorId=identity).one_or_none()


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict):
    """
    Called automatically when jwt_required is called. Checks if the JWT's
    jit (unique identifier) is in the redis blocklist store.

    Returns:
        bool: True if the JWT is in the redis blocklist store, False otherwise.
    """
    jti = jwt_payload["jti"]
    token_in_redis = jwt_redis_blocklist.get(jti)
    return token_in_redis is not None


def new_instructor(email, password, fname, lname):
    """
    Creates a new instructor in the database with the given email, password, first name, and last name.

    Args:
        email (str): The email address of the new instructor.
        password (str): The password of the new instructor.
        fname (str): The first name of the new instructor.
        lname (str): The last name of the new instructor.

    Returns:
        Instructor: The newly created Instructor object.

    Raises:
        Exception: If there was an error adding the new instructor to the database.
    """
    salt = make_salt()
    hash_password = make_pw_hash(email, password, salt)
    try:
        instructor = Instructor(
            firstName=fname,
            lastName=lname,
            email=email.lower(),
            userPassword=hash_password,
            passwordSalt=salt,
            created=datetime.utcnow(),
            lastLogin=None,
            frequencyId=2,  # default to weekly scan frequency for new users
        )

        db.session.add(instructor)
        db.session.commit()
        logger.info("New instructor created: %s", email)
        return instructor
    except Exception as e:
        db.session.rollback()
        logger.error("Error creating new instructor: %s", e)
        raise e


def make_salt(length=120):
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


def make_pw_hash(email, pw, salt=None):
    if not salt:
        salt = make_salt()
    to_encode = str(email + pw + salt).encode("utf-8")
    hashed = hashlib.sha256(to_encode).hexdigest()
    return hashed


def valid_email(email):
    if len(email) > 7:
        # email must end in ncsu.edu

        if email[-8:] != "ncsu.edu":
            return False

        if (
            re.match(r"^([a-zA-Z0-9._%-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$", email)
            is not None
        ):
            return True
    return False


def valid_password(password):
    if len(password) > 6 and " " not in password:
        return True
    return False


def verify_password(password, confirmed_password):
    return password == confirmed_password and confirmed_password != ""
