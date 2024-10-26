import uuid
from flask import Blueprint, request
from flask_mailing import Message

from .auth import make_pw_hash, make_salt, valid_password, verify_password
from extensions import mail, redis_pw_reset_token_store, logger, db
from models.models import Instructor
from config import HOST

emails = Blueprint("emails", __name__)


@emails.route("/resetpassword", methods=["POST"])
async def request_password_reset():
    """
    Sends password reset email to user given a valid email.
    """
    try:
        data = request.json
        recipient = data.get("recipient")

        logger.info(f"Reset password request for {recipient}")

        instructor = Instructor.query.filter_by(email=recipient).one_or_none()
        if not instructor:
            return {"message": "Email not found"}, 404

        
        msg = Message(
            subject="Password Reset - WolfWatch",
            recipients=[recipient],
        )

        reset_token = uuid.uuid4().hex
        redis_pw_reset_token_store.set(reset_token, instructor.instructorId, ex=3600)

        msg.body = f"""
Hello {instructor.firstName},

You have requested to reset your password for WolfWatch. Please click the link below to reset your password.

https://{HOST}/password-reset/{reset_token} - This link will expire in 1 hour.

If you did not request to reset your password, please ignore this email.

Thank you,

WolfWatch Team
        """

        await mail.send_message(msg)
        logger.info(f"Reset password email sent to {recipient[0:3]}...")
        return {"message": "Email sent successfully"}, 200
    except:
        logger.exception(f"Reset password email failed to send to {recipient[0:3]}...")
        return {"message": "Email failed to send"}, 500


@emails.route("/resetpassword", methods=["DELETE"])
def reset_password():
    """
    Resets user password given a valid reset token.
    """
    try:
        data = request.json

        new_password = data.get("newPassword")
        confirmed_new_password = data.get("confirmedNewPassword")
        token = data.get("resetToken")

        if not new_password or not confirmed_new_password or not token:
            return {"message": "Missing required fields"}, 400

        instructor_id = redis_pw_reset_token_store.get(token)
        instructor = Instructor.query.filter_by(
            instructorId=instructor_id
        ).one_or_none()

        if not instructor:
            return {"message": "Reset token is invalid or expired"}, 404

        if not valid_password(new_password):
            return {"message": "Invalid password"}, 400

        if not verify_password(new_password, confirmed_new_password):
            return {"message": "Passwords do not match"}, 400

        new_salt = make_salt()
        new_password_hash = make_pw_hash(instructor.email, new_password, new_salt)

        if (
            make_pw_hash(instructor.email, new_password, instructor.passwordSalt)
            == instructor.userPassword
        ):
            return {
                "message": "New password cannot be the same as the old password"
            }, 400

        instructor.passwordSalt = new_salt
        instructor.userPassword = new_password_hash

        db.session.add(instructor)
        db.session.commit()

        redis_pw_reset_token_store.delete(token)

        logger.info(f"Password reset for {instructor.email[0:3]}...")
        return {"message": "Password reset successfully"}, 200
    except:
        logger.exception(f"Failed to reset password.")
        return {"message": "Failed to reset password."}, 500
    