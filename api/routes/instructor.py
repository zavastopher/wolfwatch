from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    jwt_required,
    current_user,
)
import requests

from extensions import db, logger
from models.models import Instructor, Assignment, Frequency
from config import SCHEDULER_URL, SCAN_FREQUENCIES

instructor = Blueprint("instructor", __name__)


@instructor.route("/", methods=["GET"])
@jwt_required()
def get_instructor():
    """
    GET: Returns the instructor's information
    """
    try:
        instructor = Instructor.query.filter(
            Instructor.instructorId == current_user.instructorId
        ).one_or_none()
        if not instructor:
            logger.warning(f"Instructor with ID {current_user.instructorId} not found.")
            return jsonify({"msg": "Instructor not found"}), 404
        return jsonify(instructor.as_dict())
    except Exception as e:
        logger.error(f"Error retrieving instructor with ID {current_user.instructorId}. Exception: {e}")
        return jsonify({"msg": "Error retrieving instructor information"}), 500


@instructor.route("/edit", methods=["PUT"])
@jwt_required()
def edit_instructor():
    """
    PUT: Edit the instructor's information
    """
    try:
        instructor = Instructor.query.filter(
            Instructor.instructorId == current_user.instructorId
        ).one_or_none()
        if not instructor:
            logger.warning(f"Instructor with ID {current_user.instructorId} not found.")
            return jsonify({"msg": "Instructor not found"}), 404
        if request.method == "PUT":
            data = request.get_json()
            firstName = data.get("firstName")
            lastName = data.get("lastName")
            email = data.get("email")
            notificationFrequency = data.get("notificationFrequency")
            if firstName:
                instructor.firstName = firstName
            if lastName:
                instructor.lastName = lastName
            if email:
                instructor.email = email
            current_frequency = Frequency.query.filter(Frequency.term == SCAN_FREQUENCIES[current_user.frequencyId].upper()).one_or_none()
            if notificationFrequency != current_frequency:
                # update all active scan jobs with new frequency
                instructor.frequencyId = Frequency.query.filter(Frequency.term == notificationFrequency.upper()).one_or_none().frequencyId
                
                assignments = Assignment.query.filter(Assignment.instructorId == current_user.instructorId).all()
                for assignment in assignments:
                    task_data = {
                        "id": assignment.assignmentId,
                        "platform": "Chegg",
                        "frequency": SCAN_FREQUENCIES[current_user.frequencyId],
                        "keywords": assignment.get_key_phrases(),
                        "textToSearch": assignment.contents,
                        "oldFrequency": current_frequency.term.capitalize(),
                    }
                    try:
                        requests.put(SCHEDULER_URL, json=task_data)
                    except Exception as e:
                        logger.info(f"Error updating scan task for assignment {assignment.assignmentId} to scheduling server: %s", e)
                        return jsonify(assignment.as_api_response())

            db.session.commit()
            logger.info(f"Instructor with ID {current_user.instructorId} updated successfully.")
            return jsonify(instructor.as_dict())
        return jsonify({"msg": "Method not allowed"}), 405
    except Exception as e:
        logger.error(f"Error updating instructor with ID {current_user.instructorId}. Exception: {e}")
        return jsonify({"msg": "Error updating instructor information"}), 500
