import time
from typing import Dict, List
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import datetime
import requests
import json
import pyperclip as pc
import time


from Scraper import Scraper
from extensions import logger

# Number of results to scan
RESULTS_TO_SCAN = 1
# The scan results endpoint URL
RESULTS_API_URL = "http://api:3001/results"

# Subclass of Scraper that contains all the properties and functionality to scrape the Chegg website.
class Chegg_Scraper(Scraper):
    # URL of the website to be scraped
    __url: str
    # List of keywords to be used to strengthen text similarity score
    __keywords: List[str]
    # Text to be scanned for
    __text_to_search: str

    # Initializes the Chegg_Scraper object with the given parameters.
    def __init__(self, keywords: List[str], text_to_search: str):
        super(Chegg_Scraper, self).__init__(keywords, text_to_search)
        self.__keywords = keywords
        self.__text_to_search = text_to_search

    # Top-level scrape function, which tries to detect which layout of Chegg is currently present and scrapes accordingly.
    def scrape(self, assignment_id):
        # Tries scraping new site first
        scrape_new_site = self.scrape_new_site(assignment_id)
        scrape_old_site = None
        # If scraping new site fails, then scrape old site
        if scrape_new_site == False:
            time.sleep(3)
            scrape_old_site = self.scrape_old_site(assignment_id)
        # If scraping both layouts are unsuccessful then return false and abort
        if scrape_new_site == False and scrape_old_site == False:
            return False
        # If one scrape is successful then return true
        return True

    # Function for scraping the old layout of Chegg.
    # Resources:
    # https://www.selenium.dev/documentation/webdriver/waits/#explicit-waits
    # https://www.selenium.dev/documentation/webdriver/elements/finders/
    # https://www.selenium.dev/documentation/webdriver/elements/interactions/#click
    # https://www.selenium.dev/documentation/webdriver/interactions/navigation/
    def scrape_old_site(self, assignment_id):
        scan_results = []
        # Initializes the Chrome webdriver with driver options
        driver = webdriver.Chrome(options=self.get_driver_options())
        self.set_driver(driver)
        # Part of disabling webdriver automation indicator flags
        self.get_driver().execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        # Sets the URL of the website using what is generated from the URL builder function and starts the driver at that URL
        self.set_url(self.url_builder(self.__text_to_search))
        self.get_driver().get(self.get_url())

        # This is under a try except structure because a TimeoutException or NoSuchElementException may be thrown
        try:
            # Check if the Solutions tab of search results exists, else timeout after 25 seconds
            element = WebDriverWait(self.get_driver(), 25).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//a[@data-test='search-tabs-link-study']")
                )
            )
            time.sleep(3)
            # Click Solutions tab
            element.click()
            # Check if the first search result exists, else timeout after 8 seconds
            element = WebDriverWait(self.get_driver(), 8).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//span[@data-test='section-1-serp-result-1-study-question']",
                    )
                )
            )

            # Grab the number of search results and print it
            element = self.get_driver().find_element(
                By.XPATH, "//div[@data-test='search-result-count-line']"
            )
            num_of_results = element.text.split()[0]
            print("Number of results: " + num_of_results + "\n")
            time.sleep(3)

            # Go through each search result to check for cheating
            for idx in range(1, RESULTS_TO_SCAN + 1):
                # Identifies each search result link
                element = self.get_driver().find_element(
                    By.XPATH,
                    f"//a[@data-test='section-1-serp-result-{idx}-study-link']",
                )
                time.sleep(3)
                # Clicks on search result link
                element.click()
                # Outsource scraping each search result to this helper function
                self.scrape_old_search_result(scan_results, assignment_id)
            # Try to post scan results to the scan results endpoint, else log error
            try:
                headers={'Content-type':'application/json', 'Accept': 'text/plain'}
                requests.post(
                    RESULTS_API_URL,
                    data=json.dumps(scan_results),
                    headers=headers,
                )
            except requests.exceptions.RequestException as e:
                logger.error("Error posting scan results to API: %s", e)
        # Catch TimeoutException and blame it on captcha
        except TimeoutException as e:
            print(f"Captcha hit for assignment {assignment_id}\n")
            logger.error(f"Captcha hit for assignment {assignment_id}\n {e}")
            # self.get_driver().quit()
            return False
        # Catch NoSuchElementException
        except NoSuchElementException as e:
            print(f"Element not found for assignment {assignment_id}\n")
            logger.error(f"Element not found for assignment {assignment_id}\n {e}")
            # self.get_driver().quit()
            return False
        # finally:
            # self.get_driver().quit()
        return True

    # Helper function for scraping each search result
    def scrape_old_search_result(self, scan_results, assignment_id):
        # Try except structure used to catch Timeout- and NoSuchElement- Exceptions.
        try:
            # Check if transcribed image text button exists, else timeout after 8 seconds
            element = WebDriverWait(self.get_driver(), 8).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@data-test='transcribed-data-text']")
                )
            )
            # Grab the actual transcribed image text
            element = self.get_driver().find_element(
                By.XPATH,
                "//div[@class='styled__TextContent-sc-1k7k16x-4 IUHUF']",
            )
        # No transcribed image text, so grab the text from question body
        except TimeoutException:
            element = WebDriverWait(self.get_driver(), 8).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@data-test='qna-question-body']")
                )
            )
        # No transcribed image text, so grab the text from question body
        except NoSuchElementException:
            element = WebDriverWait(self.get_driver(), 8).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@data-test='qna-question-body']")
                )
            )
        # Get the current URL for scan results
        current_url = self.get_driver().current_url
        # Get the text similarity score for this scan result
        text_similarity_score = (
            self.calc_text_similarity(
                self.__text_to_search, element.text, self.__keywords
            )
            * 100
        )
        # Construct scan result dictionary
        scan_result_data = {
            "confidenceProbability": text_similarity_score,
            "url": current_url,
            "scanTime": int(datetime.datetime.now().timestamp()),
            "assignmentId": assignment_id,
        }
        # Append to scan results list
        scan_results.append(scan_result_data)
        logger.info(
            "Found a match for assignment %s - %s",
            assignment_id,
            current_url,
        )
        time.sleep(3)
        # Navigate back a page
        self.get_driver().back()
        time.sleep(3)

    # Function to scrape the new layout of Chegg
    def scrape_new_site(self, assignment_id):
        scan_results = []
        num_of_results = 0
        driver = webdriver.Chrome(options=self.get_driver_options())
        self.set_driver(driver)
        self.get_driver().execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        self.set_url("https://www.chegg.com/chat")
        self.get_driver().get(self.get_url())
        element = None
        try:
            element = WebDriverWait(self.get_driver(), 25).until(
                EC.presence_of_element_located((By.XPATH, "//div[@id='editor01-']"))
            )
            print(f"New Site Found Reattempting for old site for assignment {assignment_id}\n")
        except TimeoutException as e:
            print(f"New Site not found for assignment {assignment_id}\n")
            logger.error(f"New Site not found for assignment {assignment_id}\n {e}")
            # self.get_driver().quit()
        return False
        # Due to the nature of Docker not using a desktop environment we cannot use copy paste
        # Functionality. A different solution for running Chrome would be required for this to be viable
        # As the new site is dynamically generated to circumvent botting.
        # This could should work on any system that can use a Non-Headles browser for scraping.
        # try:
        #     pc.copy(self.__text_to_search)
        #     element.send_keys(Keys.CONTROL, 'v')
        #     time.sleep(3)
        #     element = self.get_driver().find_element(By.XPATH, "//button[@data-test='nonsub-unified-input-component-submit-button']")
        #     element.click()
        #     try:
        #         element = WebDriverWait(self.get_driver(), 8).until(
        #             EC.presence_of_element_located(
        #                 (
        #                     By.XPATH,
        #                     "//*[@id='message-1']/div/section/div[2]/div"
        #                 )
        #             )
        #         )
        #         num_of_results = int(element.text.split()[2])
        #     except TimeoutException:
        #         self.scrape_new_search_result(scan_results, assignment_id)
        #     for idx in range(0, num_of_results):
        #         element = WebDriverWait(self.get_driver(), 8).until(
        #             EC.presence_of_element_located(
        #                 (
        #                     By.XPATH,
        #                     f"//a[@data-test='undefined-search-results-result-{idx}']"
        #                 )
        #             )
        #         )
        #         time.sleep(3)
        #         self.get_driver().execute_script("arguments[0].click();", element)
        #         self.scrape_new_search_result(scan_results, assignment_id)
        #         time.sleep(3)
        #         self.get_driver().back()
        #         time.sleep(3)
        #     try:
        #         requests.post(
        #             RESULTS_API_URL,
        #             json=json.dumps(scan_results),
        #         )
        #     except requests.exceptions.RequestException as e:
        #         logger.error("Error posting scan results to API: %s", e)
        # except TimeoutException as e:
        #     print(f"Captcha hit for assignment {assignment_id}\n")
        #     logger.error(f"Captcha hit for assignment {assignment_id}\n {e}")
        #     # self.get_driver().quit()
        #     return False
        # except NoSuchElementException as e:
        #     print(f"Element not found for assignment {assignment_id}\n")
        #     logger.error(f"Element not found for assignment {assignment_id}\n {e}")
        #     # self.get_driver().quit()
        #     return False
        # # finally:
        #     # self.get_driver().quit()
        # return True

    # def scrape_new_search_result(self, scan_results, assignment_id):
    #     search_result_text = ""
    #     element = WebDriverWait(self.get_driver(), 8).until(
    #         EC.presence_of_element_located(
    #             (
    #                 By.XPATH, 
    #                 "//div[@data-test='qna-question-body']"
    #             )
    #         )
    #     )
    #     search_result_text += element.text
    #     try:
    #         element = WebDriverWait(self.get_driver(), 8).until(
    #             EC.presence_of_element_located(
    #                 (
    #                     By.XPATH, 
    #                     "//*[@id='question-transcript']/div"
    #                 )
    #             )
    #         )
    #         search_result_text += " " + element.text
    #     except TimeoutException:
    #         print("No image to transcribe")
    #         pass
    #     current_url = self.get_driver().current_url
    #     text_similarity_score = (
    #         self.calc_text_similarity(
    #             self.__text_to_search, search_result_text, self.__keywords
    #         )
    #         * 100
    #     )
    #     scan_result_data = {
    #         "confidenceProbability": text_similarity_score,
    #         "url": current_url,
    #         "scanTime": f'{datetime.datetime.now()}',
    #         "assignmentId": assignment_id,
    #     }
    #     scan_results.append(scan_result_data)
    #     logger.info(
    #         "Found a match for assignment %s - %s",
    #         assignment_id,
    #         current_url,
    #     )

    def url_builder(self, search_query: str):
        return "https://www.chegg.com/search?q=" + search_query
