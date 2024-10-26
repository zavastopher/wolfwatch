from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    jwt_required,
    current_user,
)
import requests

from extensions import db, logger
from models.models import Assignment, KeyPhrase, Frequency
from config import SCHEDULER_URL, SCAN_FREQUENCIES, SCHEDULER_RUN_URL

assignments = Blueprint("assignments", __name__)


@assignments.route("/", methods=["POST"])
@jwt_required()
def create_assignment():
    """Creates a new assignment."""
    data = request.json
    try:
        dueDate = datetime.strptime(data.get("dueDate"), "%Y-%m-%dT%H:%M:%S.%fZ")
        validate_assignment_data(
            dueDate, data.get("contents"), data.get("courseName"), data.get("title")
        )

        assignment = Assignment(
            assignmentActive=True,
            dueDate=dueDate,
            contents=data.get("contents"),
            courseName=data.get("courseName"),
            title=data.get("title"),
            instructorId=current_user.instructorId,
            lastNotificationCheck=datetime.utcnow(),
        )
        db.session.add(assignment)
        db.session.commit()
        keyPhrases = add_key_phrases(data.get("keyPhrases"), assignment.assignmentId)

        # Add task to scheduling queue
        task_data = {
            "id": assignment.assignmentId,
            "platform": "Chegg",
            "frequency": SCAN_FREQUENCIES[current_user.frequencyId],
            "keywords": keyPhrases,
            "textToSearch": assignment.contents,
        }
        try:
            requests.post(SCHEDULER_URL, json=task_data)
        except Exception as e:
            logger.info("Error sending post request to scraping server: %s", e)
            return jsonify(assignment.as_api_response())

        logger.info("New assignment created: %s", data.get("title"))
        return jsonify(assignment.as_api_response()), 201
    except Exception as e:
        logger.error(f"Error creating assignment. Exception: {e}")
        return jsonify({"msg": "Error creating assignment"}), 400


@assignments.route("/", methods=["GET"])
@jwt_required()
def fetch_assignments():
    """Returns a list of assignments for the current user's instructor ID."""
    try:
        assignments = Assignment.query.filter(
            Assignment.instructorId == current_user.instructorId
        )
        return (
            jsonify([assignment.as_api_response() for assignment in assignments]),
            200,
        )
    except Exception as e:
        logger.error(f"Error fetching assignments. Exception: {e}")
        return jsonify({"msg": "Error fetching assignments"}), 400


@assignments.route("/<int:assignment_id>/scan", methods=["POST"])
@jwt_required()
def scan_now(assignment_id):
    try:
        assignment = get_assignment_by_id(assignment_id)
        if not assignment:
            return jsonify({"msg": "Assignment not found"}), 404

        if assignment.instructorId != current_user.instructorId:
            return jsonify({"msg": "Unauthorized"}), 401
        
        try:
            requests.post(SCHEDULER_RUN_URL, json={
                "assignmentId": assignment_id,
                "contents": assignment.contents,
                "keywords": assignment.get_key_phrases(),
            })
        except Exception as e:
            logger.info("Error sending post request to scraping server: %s", e)
            return jsonify(assignment.as_api_response())

        logger.info("Assignment scanned on demand: %s", assignment.title)
        return jsonify(assignment.as_api_response()), 201
    except Exception as e:
        logger.info("Error scanning assignment now: %s", e)
        return jsonify({"msg": "Error scanning assignment"}), 400

def validate_assignment_data(dueDate, contents, courseName, title):
    if dueDate < datetime.utcnow():
        raise ValueError("Due date must be in the future")
    if not contents:
        raise ValueError("Assignment text cannot be empty")
    if not courseName:
        raise ValueError("Course name cannot be empty")
    if not title:
        raise ValueError("Title cannot be empty")


def add_key_phrases(keyPhrases, assignment_id):
    if keyPhrases:
        for keyPhrase in keyPhrases:
            keyPhraseObject = KeyPhrase(
                assignmentId=assignment_id,
                keyPhraseText=keyPhrase,
            )
            db.session.add(keyPhraseObject)
        db.session.commit()
        return keyPhrases
    return None


@assignments.route("/<int:assignment_id>", methods=["GET", "PUT", "DELETE"])
@jwt_required()
def interact_with_assignment(assignment_id):
    """
    Get, update, or delete an assignment by ID.
    Args:
        assignment_id (int): The ID of the assignment to get, update, or delete.
    """
    assignment = get_assignment_by_id(assignment_id)
    if not assignment:
        return jsonify({"msg": "Assignment not found"}), 404

    if assignment.instructorId != current_user.instructorId:
        return jsonify({"msg": "Unauthorized"}), 401

    if request.method == "PUT":
        return update_assignment(assignment)
    elif request.method == "DELETE":
        return delete_assignment(assignment)
    else:
        return jsonify(assignment.as_api_response())


def get_assignment_by_id(assignment_id):
    try:
        return Assignment.query.filter(
            Assignment.assignmentId == assignment_id
        ).one_or_none()
    except Exception as e:
        logger.error(
            f"Error retrieving assignment with id: {assignment_id}. Exception: {e}"
        )
        return None


def update_assignment(assignment):
    data = request.json
    # date in format: Fri, 17 Nov 2023 05:00:00 GMT

    dueDate = datetime.strptime(data.get("dueDate"), "%Y-%m-%dT%H:%M:%S.%fZ")
    if dueDate < datetime.utcnow():
        return jsonify({"msg": "Due date must be in the future"}), 400

    contents, courseName, title = (
        data.get("contents"),
        data.get("courseName"),
        data.get("title"),
    )
    if not all([contents, courseName, title]):
        return (
            jsonify({"msg": "Assignment text, course name, or title cannot be empty"}),
            400,
        )

    active = data.get("assignmentActive")
    logger.info("Assignment active status changed from %s to %s", assignment.assignmentActive, active)
    
    if active is False and assignment.assignmentActive is True:
        task_data = {
        "id": assignment.assignmentId,
        "platform": "Chegg",
        "frequency": SCAN_FREQUENCIES[current_user.frequencyId],
        "keywords": None,
        "textToSearch": assignment.contents,
        }

        try:
            requests.delete(SCHEDULER_URL, json=task_data)
            logger.info("Removed scan for assignment: %s", assignment.title)
        except Exception as e:
            logger.info("Error sending delete request to scraping server", e)
            return jsonify(assignment.as_api_response())
    elif active is True and assignment.assignmentActive is False:
        task_data = {
        "id": assignment.assignmentId,
        "platform": "Chegg",
        "frequency": SCAN_FREQUENCIES[current_user.frequencyId],
        "keywords": assignment.get_key_phrases(),
        "textToSearch": assignment.contents,
        }

        try:
            requests.post(SCHEDULER_URL, json=task_data)
            logger.info("Added scan for assignment: %s", assignment.title)
        except Exception as e:
            logger.info("Error sending post request to scraping server", e)
            return jsonify(assignment.as_api_response())
        
    if active is not None:
        assignment.assignmentActive = active

    assignment.dueDate = dueDate
    assignment.contents = contents
    assignment.courseName = courseName
    assignment.title = title
    assignment.instructorId = current_user.instructorId
    db.session.commit()

    update_key_phrases(assignment, data.get("keyPhrases"))
    logger.info("Assignment updated: %s", data.get("title"))

    return jsonify(assignment.as_api_response())


def update_key_phrases(assignment, keyPhrases):
    currentKeyPhrases = KeyPhrase.query.filter(
        KeyPhrase.assignmentId == assignment.assignmentId
    ).all()

    for currentKeyPhrase in currentKeyPhrases:
        if not keyPhrases or currentKeyPhrase.keyPhraseText not in keyPhrases:
            db.session.delete(currentKeyPhrase)
        else:
            keyPhrases.remove(currentKeyPhrase.keyPhraseText)

    if keyPhrases:
        for keyPhrase in keyPhrases:
            keyPhraseObject = KeyPhrase(
                assignmentId=assignment.assignmentId,
                keyPhraseText=keyPhrase,
            )
            db.session.add(keyPhraseObject)

    db.session.commit()


def delete_assignment(assignment):
    db.session.delete(assignment)
    db.session.commit()

    task_data = {
        "id": assignment.assignmentId,
        "platform": "Chegg",
        "frequency": SCAN_FREQUENCIES[current_user.frequencyId],
        "keywords": None,
        "textToSearch": assignment.contents,
    }
    try:
        requests.delete("http://scheduler:3002/schedule_task", json=task_data)
    except Exception as e:
        print("Error sending delete request to scraping server", e)
        return jsonify(assignment.as_api_response())

    logger.info("Assignment deleted: %s", assignment.title)
    return jsonify({"msg": "Assignment deleted"})
