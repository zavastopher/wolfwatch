import os

# == Flask app configuration ==
APP_ENVIRONMENT = os.getenv(
    "APPLICATION_ENVIRONMENT", "production"
)  # [development, production]
DEBUG = APP_ENVIRONMENT == "development"
SECRET_KEY = os.getenv("APPLICATION_SECRET_KEY")
HOST = os.getenv("APPLICATION_HOST", "0.0.0.0")
PORT = os.getenv("APPLICATION_PORT", 3001)
SCHEDULER_URL = os.environ.get("SCHEDULER_URL", "http://scheduler:3002/schedule_task")
SCHEDULER_RUN_URL="http://scheduler:3002/run_task"
MINIMUM_CONFIDENCE = float(os.environ.get("APPLICATION_MIN_CONFIDENCE", 80.0))
SCAN_FREQUENCIES = {
    1: "Monthly",
    2: "Weekly",
    3: "Daily",
}

# == Mail configuration ==
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 465
MAIL_DEBUG = DEBUG
MAIL_USERNAME = os.getenv("APPLICATION_MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("APPLICATION_MAIL_PASSWORD")
MAIL_DEFAULT_SENDER = os.getenv("APPLICATION_MAIL_DEFAULT_SENDER")
MAIL_USE_TLS = False
MAIL_USE_SSL = True

# == Redis configuration ==
REDIS_HOST = os.getenv("APPLICATION_REDIS_HOST", "redis")
REDIS_PORT = os.getenv("APPLICATION_REDIS_PORT", 6379)
REDIS_BLOCKLIST_DB = os.getenv(
    "APPLICATION_TOKEN_BLOCKLIST_REDIS_DB", 0
)  # 0 is the redis db for the jwt blocklist

# == JWT configuration ==
COOKIE_EXPIRATION = 3600  # Exp time for cookie containing JWT in seconds
COOKIE_SECURE = (
    APP_ENVIRONMENT == "production"
)  # restrict cookie to https (only in prod)
TOKEN_EXPIRATION = 3600  # Expiration time for JWT in seconds
TOKEN_LOCATION = ["cookies"]  # Where to look for JWTs by default
SESSION_COOKIE = False

# == Database configuration ==
DATABASE_URI = os.getenv("APPLICATION_DATABASE_URI")
TRACK_MODIFICATIONS = False
