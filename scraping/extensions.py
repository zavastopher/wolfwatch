import logging
from logging.handlers import RotatingFileHandler
import os
from celery import Celery

# Got help from:
# https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/redis.html
# https://docs.celeryq.dev/en/stable/getting-started/first-steps-with-celery.html#keeping-results
# Create Celery instance and specify the broker and backend
celery = Celery(
    "TaskScheduler",
    broker="redis://redis:6379/1",
    backend="redis://redis:6379/1",
)
# Set Celery Beat to wake up in 30 seconds max
celery.conf.update(
    beat_max_loop_interval=30,
)
# Logger initialization
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
