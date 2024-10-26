from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
from typing import Dict, List
from abc import ABC, abstractmethod
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import scipy

# Superclass to potentially multiple platform-specific subclasses.
# This class contains all of the common properties and functionality that can be used for scraping any homework help website.
class Scraper(ABC):
    # ID of the instance
    __id: int
    # URL of the website to be scraped
    __url: str
    # List of keywords to be used to strengthen text similarity score
    __keywords: List[str]
    # Text to be scanned for
    __text_to_search: str
    # User agent to be used when scraping
    __user_agent: str
    # Customizations to the webdriver
    __driver_options: Options
    # Webdriver to be used to scrape
    __driver: webdriver

    # Got help from:
    # https://www.zenrows.com/blog/selenium-avoid-bot-detection#disable-automation-indicator-webdriver-flags
    # Other resources:
    # https://www.selenium.dev/documentation/webdriver/browsers/chrome/
    # This function sets up what you might need to start a scraping session.
    def __init__(self, keywords: List[str], text_to_search: str):
        self.__keywords = keywords
        self.__text_to_search = text_to_search
        # Utilizing a single user agent to seem more natural
        self.__user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        # Driver options object
        options = Options()
        # options.headless = False

        # These options are set to disable automation indicator web driver flags, which helps prevent bot detection.
        options.add_argument("--disable-blink-features=AutomationControlled")  #
        options.add_experimental_option("excludeSwitches", ["enable-automation"])  #
        options.add_experimental_option("useAutomationExtension", False)  #
        options.add_argument("--start-maximized")  #

        # Set the user agent
        options.add_argument(f"--user-agent={self.__user_agent}")
        # Disable sandboxing, which prevents browser from running in a restricted environment.
        options.add_argument("--no-sandbox")
        # Set the window size
        options.add_argument("--window-size=1920, 1080")
        # Make browser headless, meaning the browser UI is not shown.
        options.add_argument("--headless")
        # Disable GPU hardware acceleration
        options.add_argument("--disable-gpu")
        # Disable shared memory usage for storing temporary files
        options.add_argument("--disable-dev-shm-usage")
        # Set the browser clipboard sharing preferences
        options.add_experimental_option('prefs', {
            'profile.default_content_setting_values': {
                'clipboard': 1
            }
        })

        # Set up the rotating proxies to work with the webdriver
        proxy = "us.smartproxy.com:10000"
        options.add_argument(f"--proxy-server={proxy}")

        # Set the driver options
        self.set_driver_options(options)

    # Sets the URL of the website to be scraped.
    def set_url(self, url: str):
        self.__url = url

    # Gets the URL of the website to be scraped.
    def get_url(self):
        return self.__url

    # Sets the keywords to be emphasized in the text similarity score.
    def set_keywords(self, keywords: List[str]):
        self.__keywords = keywords

    # Gets the keywords to be emphasized in the text similarity score.
    def get_keywords(self):
        return self.__keywords

    # Sets the text to be scanned for.
    def set_text_to_search(self, text_to_search: str):
        self.__text_to_search = text_to_search

    # Gets the text to be scanned for.
    def get_text_to_search(self):
        return self.__text_to_search

    # Sets the user agent to be used for the scraping session.
    def set_user_agent(self, user_agent: str):
        self.__user_agent = user_agent

    # Gets the user agent to be used for the scraping session.
    def get_user_agent(self):
        return self.__user_agent

    # Sets the driver options to be used with the webdriver.
    def set_driver_options(self, driver_options: Options):
        self.__driver_options = driver_options

    # Gets the driver options to be used with the webdriver.
    def get_driver_options(self):
        return self.__driver_options

    # Sets the webdriver.
    def set_driver(self, driver: webdriver):
        self.__driver = driver

    # Gets the webdriver.
    def get_driver(self):
        return self.__driver

    # URL constructor to be implemented for each scraper subclass.
    @abstractmethod
    def url_builder(self, search_query: str):
        pass

    # Got help from:
    # https://spotintelligence.com/2022/12/19/text-similarity-python/
    # This function generates a text similarity score given 2 pieces of text and any keywords to emphasize.
    def calc_text_similarity(self, text_1: str, text_2: str, keywords: List[str]):
        # Stores the final similarity score
        similarity_score = -1
        # Initialize a TF-IDF vectorizer
        text_vectorizer = TfidfVectorizer()
        # Fit it to text 1 and 2 to create TF-IDF feature vectors
        text_vectors = text_vectorizer.fit_transform([text_1, text_2])
        # 2 paths: if there are keywords provided and if there are no keywords provided
        if keywords != None:
            # Initialize a TF-IDF vectorizer with vocabulary from text_vectorizer
            keyword_vectorizer = TfidfVectorizer(
                vocabulary=text_vectorizer.get_feature_names_out()
            )
            # Convert keywords into TF-IDF vector
            keyword_vector = keyword_vectorizer.fit_transform([" ".join(keywords)])
            # Get the number of rows in text_vectors
            text_num_rows = text_vectors.shape[0]
            # Make keyword_vector match the number of rows in text_vectors
            keyword_vector = scipy.sparse.vstack([keyword_vector] * text_num_rows)
            # Combine keyword_vector and text_vectors
            combined_vectors = scipy.sparse.hstack([text_vectors, keyword_vector])
            # Generate similarity score using cosine similarity function
            similarity = cosine_similarity(combined_vectors[0], combined_vectors[1])
            # Update final similarity score variable
            similarity_score = similarity[0][0]
        else:
            # Calculate similarity score using cosine similarity function of just the text_vectors
            similarity = cosine_similarity(text_vectors)
            # Update final similarity score variable
            similarity_score = similarity[0][0]
        return similarity_score