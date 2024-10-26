from .auth import auth
from .assignments import assignments
from .results import results
from .instructor import instructor
from .emails import emails


def register_blueprints(app):
    """
    Register the provided blueprints with the Flask application.

    Args:
        app (Flask): The Flask application instance to which blueprints should be registered.
    """
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(assignments, url_prefix="/assignments")
    app.register_blueprint(results, url_prefix="/results")
    app.register_blueprint(instructor, url_prefix="/instructor")
    app.register_blueprint(emails, url_prefix="/emails")
