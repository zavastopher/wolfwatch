from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    jwt_required,
    current_user,
)
import socket
from flask_mailing import Message
import pytz
import json

from extensions import db, logger, mail
from models.models import ScanResult, Assignment, Instructor
from config import MINIMUM_CONFIDENCE

results = Blueprint("results", __name__)


@results.route("/", methods=["GET"])
@jwt_required()
def get_results():
    """
    Returns a list of scan results that belong to the user's assignments. Only assignments that
    meet or exceed the minimum confidence threshold will be sent.
    """
    try:
        results = (
            db.session.query(ScanResult)
            .join(Assignment, ScanResult.assignmentId == Assignment.assignmentId)
            .filter(Assignment.instructorId == current_user.instructorId)
            .filter(ScanResult.confidenceProbability >= MINIMUM_CONFIDENCE)
            .all()
        )
        logger.info(
            f"Retrieved scan results for instructor with ID {current_user.instructorId}."
        )
        return jsonify([result.as_dict() for result in results])
    except Exception as e:
        logger.error(
            f"Error retrieving scan results for instructor with ID {current_user.instructorId}. Exception: {e}"
        )
        return jsonify({"msg": "Error retrieving scan results"}), 500


@results.route("/", methods=["POST"])
async def add_scan_result():
    """
    Add a scan result(s) to the database and send a notification to the instructor
    if the confidence probability is above the minimum threshold.
    """
    # only accept requests from the scraper worker
    scraper_worker_addr = socket.gethostbyname("celery_worker")
    if request.remote_addr != scraper_worker_addr:
        return jsonify({"msg": "Unauthorized"}), 401
    try:
        logger.info(request.json)
        logger.info(request.get_json())
        results = request.get_json()
        instructor_email = None
        for result in results:
            confidence = float(result.get("confidenceProbability"))
            url = result.get("url")
            scantime = datetime.fromtimestamp(result.get("scanTime"), tz=pytz.utc).astimezone(pytz.timezone('US/Eastern'))
            assignmentId = result.get("assignmentId")

            # check if result already exists in database
            existing_result = ScanResult.query.filter(
                ScanResult.url == url, ScanResult.assignmentId == assignmentId
            ).one_or_none()

            if existing_result:
                logger.info(
                    f"Scan result for assignment with url {url} and ID {assignmentId} already exists in database."
                )
                continue

            new_result = ScanResult(
                confidenceProbability=confidence,
                url=url,
                scantime=scantime,
                assignmentId=assignmentId,
            )

            # don't notify instructor if confidence probability is below threshold
            if new_result.confidenceProbability < MINIMUM_CONFIDENCE:
                logger.info(
                    f"Scan result for assignment with ID {result.get('assignmentId')} did not meet minimum confidence threshold. Confidence: {new_result.confidenceProbability}"
                )
                db.session.add(new_result)
                continue

            # get instructor email if not already retrieved
            # (all results in a batch should have the same instructor)
            if not instructor_email:
                assignment = Assignment.query.filter(
                    Assignment.assignmentId == result.get("assignmentId")
                ).one_or_none()
                instructor_email = (
                    Instructor.query.filter(
                        Instructor.instructorId == assignment.instructorId
                    )
                    .one_or_none()
                    .email
                )

            # send email to instructor if confidence probability is above threshold
            if new_result.confidenceProbability >= MINIMUM_CONFIDENCE:
                logger.info(
                    f"Scan result for assignment with ID {result.get('assignmentId')} met minimum confidence threshold. Confidence: {new_result.confidenceProbability}"
                )

                msg = Message(
                    subject=f"Your Assignment \"{assignment.title}\" was found online - WolfWatch",
                    recipients=[instructor_email],
                )

                assignment = Assignment.query.filter(
                    Assignment.assignmentId == new_result.assignmentId
                ).one_or_none()

                msg.html = f"""
Hello,<br>
<br>
We've potentially found one of your assignments on the web:<br>
<br>
<b>Assignment</b>: {assignment.title}<br>
<b>URL of Occurance</b>: {new_result.url}<br>
<b>Confidence</b>: {new_result.confidenceProbability}%<br>
<b>Time of Detection</b>: {new_result.scantime.strftime('%m/%d/%Y %I:%M:%S %p')}<br>

<br>Please review the incident and take appropriate action.
<br>
<br>
Thanks,<br>
WolfWatch Team
"""

            await mail.send_message(msg)
            db.session.add(new_result)
            logger.info(
                f"Added scan result for assignment with ID {result.get('assignmentId')} to database."
            )

        db.session.commit()
        return jsonify({"msg": "Added new scan result(s) to database."}), 201

    except Exception as e:
        logger.error(f"Error adding scan result. Exception: {e}")
        return jsonify({"msg": "Error adding scan result"}), 500


@results.route("/<int:result_id>", methods=["GET"])
@jwt_required()
def get_result_by_id(result_id):
    """
    Get a scan result from a specified result id.
    """
    try:
        result = ScanResult.query.filter(ScanResult.scanId == result_id).one_or_none()

        if not result:
            logger.warning(f"Scan result with ID {result_id} not found.")
            return jsonify({"msg": "Result not found"}), 404

        parent_assignment = Assignment.query.filter(
            Assignment.assignmentId == result.assignmentId
        ).one_or_none()

        if (
            parent_assignment
            and parent_assignment.instructorId != current_user.instructorId
        ):
            logger.warning(
                f"Unauthorized access attempt to result with ID {result_id} by user {current_user.instructorId}."
            )
            return jsonify({"msg": "Unauthorized"}), 401

        return jsonify(result.as_dict())
    except Exception as e:
        logger.error(
            f"Error retrieving scan result with id: {result_id}. Exception: {e}"
        )
        return jsonify({"msg": "Error retrieving scan result"}), 500
