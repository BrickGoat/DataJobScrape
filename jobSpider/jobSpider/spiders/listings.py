import scrapy
import time
from selenium.webdriver.common.action_chains import ActionChains
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys

class ListingSpider(scrapy.Spider):
    name = "listing"

    def start_requests(self):
        urls = [
            "https://www.usajobs.gov/Search/Results?j=2210&j=1550&j=1560&k=data&p=1#",
            "https://www.progressivedatajobs.org/job-postings/",
            "https://outerjoin.us/?q=data",
            "https://weworkremotely.com/categories/remote-back-end-programming-jobs",
            "https://weworkremotely.com/categories/remote-full-stack-programming-jobs"
        ]
        # Selectors for getting next page
        next = [
            (By.CLASS_NAME, "usajobs-search-pagination__next-page"),
            ("rel_link", "/job-postings/?wpv_view_count=627&wpv_paged=2"),
            (By.XPATH, "(//nav//a)[0]"),
            (None, None),
            (None, None),
        ]
        # Selectors for divs containing link to job post
        listing_divs = [
            (
                By.XPATH,
                "//div[@id='usajobs-search-results']/div[@class='usajobs-search-result--core']",
            ),
            (By.CLASS_NAME, "grid-job"),
            (By.CLASS_NAME, "w-full"),
            (By.XPATH, "/article/ul/li"),
            (By.XPATH, "/article/ul/li"),
        ]
        requests = [
            self.makeRequest(
                urls[i],
                5,
                self.parsePage,
                next[i],
                listing_divs[i],
            )
            for i in range(urls)
        ]
        return requests

    def parsePage(self):
        pass