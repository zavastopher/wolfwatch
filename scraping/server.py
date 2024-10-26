import os
from flask import Flask, request, jsonify
import socket

from TaskScheduler import add_task_to_queue, remove_task_from_queue, run_scan_now, update_task_in_queue
from extensions import logger

app = Flask(__name__)
app.logger.handlers = logger.handlers
app.logger.setLevel(logger.level)

api_addr = socket.gethostbyname("api")


@app.route("/schedule_task", methods=["POST", "DELETE", "PUT"])
def schedule_task():
    if request.remote_addr != api_addr:
        return jsonify({"msg": "Unauthorized"}), 401

    data = request.json
    assignmentId = data.get("id")
    platform = data.get("platform")
    frequency = data.get("frequency")
    keywords = data.get("keywords")
    textToSearch = data.get("textToSearch")

    if request.method == "POST":
        add_task_to_queue(assignmentId, platform, frequency, keywords, textToSearch)

        logger.info(
            "%s scan scheduled for assignment %s - frequency: %s",
            platform,
            assignmentId,
            frequency,
        )
        return jsonify({"msg": "Task added to queue"}), 200
    elif request.method == "DELETE":
        remove_task_from_queue(assignmentId, platform, frequency, keywords, textToSearch)

        logger.info(
            "%s scan removed from assignment %s - frequency: %s",
            platform,
            assignmentId,
            frequency,
        )
        return jsonify({"msg": "Task removed from queue"}), 200
    elif request.method == "PUT":
        oldFrequency = data.get("oldFrequency")
        update_task_in_queue(assignmentId, platform, oldFrequency, frequency, keywords, textToSearch)

        logger.info(
            "%s scan frequency updated for assignment %s - old frequency: %s, new frequency: %s",
            platform,
            assignmentId,
            oldFrequency,
            frequency,
        )
        return jsonify({"msg": "Task updated in queue"}), 200

@app.route("/run_task", methods=["POST"])
def run_task():
    if request.remote_addr != api_addr:
        return jsonify({"msg": "Unauthorized"}), 401

    # add task to queue and run it immediately and then remove it from queue after it's done
    data = request.json
    assignmentId = data.get("assignmentId")
    contents = data.get("contents")
    keywords = data.get("keywords")

    try:
        logger.info("Running scan now for assignment %s", assignmentId)
        run_scan_now(assignmentId, "Chegg", keywords, contents)
        return jsonify({"msg": "Task ran successfully"}), 200
    except Exception as e:
        logger.error("Error running scan now for assignment %s. Exception: %s", assignmentId, e)
        return jsonify({"msg": "Error running scan now"}), 400


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=os.environ.get("SCHEDULER_SERVER_PORT", 3002),
        debug=os.environ.get("APPLICATION_ENVIRONMENT", True) == "development",
    )
