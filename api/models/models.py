from datetime import datetime
from sqlalchemy.dialects.mysql import LONGTEXT
from extensions import db
from .custom_sql_types import LONGTEXT


# Frequency Model
class Frequency(db.Model):
    __tablename__ = "frequency"
    frequencyId = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(120))


# Instructor Model
class Instructor(db.Model):
    __tablename__ = "instructor"
    instructorId = db.Column(db.Integer, primary_key=True)
    lastName = db.Column(db.String(120), name="lastName")
    firstName = db.Column(db.String(120), name="firstName")
    email = db.Column(db.String(120))
    userPassword = db.Column(db.String(120), name="userPassword")
    passwordSalt = db.Column(db.String(120), name="passwordSalt")
    created = db.Column(db.DateTime, default=datetime.utcnow())
    lastLogin = db.Column(db.DateTime)
    frequencyId = db.Column(
        db.Integer, db.ForeignKey("frequency.frequencyId"), name="frequencyId"
    )
    verified = db.Column(db.Boolean, name="verified")

    def as_dict(self):
        return {
            "firstName": self.firstName,
            "lastName": self.lastName,
            "email": self.email,
            "lastLogin": self.lastLogin,
            "notificationFrequency": Frequency.query.filter(
                Frequency.frequencyId == self.frequencyId
            )
            .one_or_none()
            .term
            if self.frequencyId
            else None,
        }


# Assignment Model
## Keeping the frequency id in the assignment table so that
class Assignment(db.Model):
    __tablename__ = "assignment"
    assignmentId = db.Column(db.Integer, primary_key=True)
    assignmentActive = db.Column(db.Boolean, name="assignmentActive")
    dueDate = db.Column(db.DateTime)
    contents = db.Column(LONGTEXT)
    courseName = db.Column(db.String(120))
    title = db.Column(db.String(120))
    lastNotificationCheck = db.Column(db.DateTime, default=datetime.utcnow())
    instructorId = db.Column(
        db.Integer, db.ForeignKey("instructor.instructorId"), name="instructorId"
    )

    def as_dict(self):
        """
        Returns an assignment and it's columns as a dictionary with fields.
        """
        return {
            "assignmentId": self.assignmentId,
            "assignmentActive": self.assignmentActive,
            "dueDate": self.dueDate.strftime("%Y-%m-%d %H:%M:%S"),
            "contents": self.contents,
            "courseName": self.courseName,
            "title": self.title,
            "lastNotificationCheck": self.lastNotificationCheck.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "instructorId": self.instructorId,
            "keyPhrases": [
                keyPhrase.as_dict()
                for keyPhrase in KeyPhrase.query.filter(
                    KeyPhrase.assignmentId == self.assignmentId
                )
            ],
        }

    def as_api_response(self):
        """
        Returns a dictionary representation of the Assignment object
        with different keys than the as_dict() method. The keys used
        here match the naming conventions used on the frontend and
        allow us to return a consistent response from the API.
        """
        return {
            "assignmentId": self.assignmentId,
            "assignmentTitle": self.title,
            "className": self.courseName,
            "dueDate": self.dueDate,
            "assignmentText": self.contents,
            "assignmentActive": self.assignmentActive,
            "lastNotificationCheck": self.lastNotificationCheck,
            "instructorId": self.instructorId,
            "keyPhrases": self.get_key_phrases(),
            "lastScan": self.get_last_scan(),
        }

    def get_key_phrases(self):
        return [
            str(keyPhrase)
            for keyPhrase in KeyPhrase.query.filter(
                KeyPhrase.assignmentId == self.assignmentId
            )
        ]
    
    def get_last_scan(self):
        scan = ScanResult.query.filter(
            ScanResult.assignmentId == self.assignmentId
        ).order_by(ScanResult.scantime.desc()).first()
        if scan:
            return scan.scantime.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return None


# ScanResult Model
class ScanResult(db.Model):
    __tablename__ = "scanResult"
    scanId = db.Column(db.Integer, primary_key=True)
    confidenceProbability = db.Column(db.Float, name="confidenceProbability")
    url = db.Column(LONGTEXT)
    assignmentId = db.Column(db.Integer, db.ForeignKey("assignment.assignmentId"))
    scantime = db.Column(db.DateTime, default=datetime.utcnow())

    def as_dict(self):
        return {
            "scanId": self.scanId,
            "confidenceProbability": self.confidenceProbability,
            "url": self.url,
            "assignment": Assignment.query.filter(
                Assignment.assignmentId == self.assignmentId
            )
            .one_or_none()
            .as_dict(),
            "scantime": self.scantime.strftime("%Y-%m-%d %H:%M:%S"),
        }


# KeyPhrase Model
class KeyPhrase(db.Model):
    __tablename__ = "keyPhrase"
    keyPhraseId = db.Column(db.Integer, primary_key=True)
    keyPhraseText = db.Column(LONGTEXT)
    assignmentId = db.Column(db.Integer, db.ForeignKey("assignment.assignmentId"))

    def as_dict(self):
        return {
            "keyPhraseId": self.keyPhraseId,
            "keyPhraseText": self.keyPhraseText,
            "assignmentId": self.assignmentId,
        }

    def __str__(self) -> str:
        return self.keyPhraseText
