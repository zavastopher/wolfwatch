from extensions import celery
from Chegg_Scraper import Chegg_Scraper
import time

# Number of tries for scraping
NUM_OF_TRIES = 5

# Always annotate each task using the format @<celery_instance_name>.task
# Task for scraping Chegg
@celery.task
def scrape_Chegg(assignment_id, keywords, text_to_search):
    print("Scraping Chegg")
    # Create Chegg Scraper object
    chegg_scraper = Chegg_Scraper(keywords, text_to_search)
    # Try scraping Chegg a total of 5 times
    for num in range(1, NUM_OF_TRIES + 1):
        # Scrape Chegg
        scrape_try = chegg_scraper.scrape(assignment_id)
        # If that scrape fails, then retry
        # Else, end task
        if scrape_try == False:
            print(f"Retrying scrape: retry #{num}")
            time.sleep(3 * num)
            pass
        else:
            print("Scrape successful")
            break