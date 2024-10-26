import time
from celery.schedules import crontab
from redbeat import RedBeatSchedulerEntry

from extensions import celery, logger
from Chegg_Scraper import Chegg_Scraper

# Number of tries for scraping
NUM_OF_TRIES = 5

# Translates frequencies to crontab
frequency_to_crontab = {
    # 2 and 5 minutes are for development purposes and should not be used in production
    "2 minute": crontab(minute="*/2"),
    "5 minutes": crontab(minute="*/5"),
    "Daily": crontab(hour="*/24"),
    "Weekly": crontab(hour="*/168"),
    "Monthly": crontab(minute="*/720"),
}

# Got help from:
# https://stackoverflow.com/questions/68888941/keyerror-received-unregistered-task-of-type-on-celery-while-task-is-registere
# Imports all the tasks in Tasks.py
celery.conf.update(imports=["Tasks"])


# Got help from:
# https://redbeat.readthedocs.io/en/latest/intro.html
# https://github.com/sibson/redbeat/issues/62
# Adds task to job queue
def add_task_to_queue(assignment_id, platform, frequency, keywords, text_to_search):
    schedule = frequency_to_crontab[frequency]
    print("Adding task to queue with schedule", schedule)

    # Construct the task to add as a RedBeatSchedulerEntry
    task_to_add = RedBeatSchedulerEntry(
        f"{assignment_id}-scrape-{platform}-{frequency}",
        f"Tasks.scrape_{platform}",
        schedule,
        args=(assignment_id, keywords, text_to_search),
        app=celery,
    )

    # Add the task
    task_to_add.save()

# Removes task from job queue
def remove_task_from_queue(assignment_id, platform, frequency, keywords, text_to_search):
    schedule = frequency_to_crontab[frequency]

    # Construct the task to remove as a RedBeatSchedulerEntry
    task_to_remove = RedBeatSchedulerEntry(
        f"{assignment_id}-scrape-{platform}-{frequency}",
        f"Tasks.scrape_{platform}",
        schedule,
        args=(assignment_id, keywords, text_to_search),
        app=celery,
    )

    # Delete the task
    task_to_remove.delete()

# Updates task with new frequency
def update_task_in_queue(assignment_id, platform, oldFrequency, frequency, keywords, text_to_search):
    schedule = frequency_to_crontab[frequency]

    # The old task to be updated
    old_task = RedBeatSchedulerEntry(
        f"{assignment_id}-scrape-{platform}-{oldFrequency}",
        f"Tasks.scrape_{platform}",
        schedule,
        args=(assignment_id, keywords, text_to_search),
        app=celery,
    )
    # Delete the old task
    old_task.delete()

    # The new task to be replaced with
    new_task = RedBeatSchedulerEntry(
        f"{assignment_id}-scrape-{platform}-{frequency}",
        f"Tasks.scrape_{platform}",
        schedule,
        args=(keywords, text_to_search),
        app=celery,
    )
    # Add the new task
    new_task.save()

# On-demand scan function
def run_scan_now(assignment_id, platform, keywords, text_to_search):
    """Runs a scan immediately"""
    celery.send_task( 
        f"Tasks.scrape_{platform}",
        args=(assignment_id, keywords, text_to_search),
    )
