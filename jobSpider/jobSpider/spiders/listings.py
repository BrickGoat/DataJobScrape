import scrapy
import time
from scrapy.shell import inspect_response
from selenium.webdriver.common.action_chains import ActionChains
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
import re

url_max_pages = {
    "usajobs": [0, 20],
    "progressivedatajobs": [0, 20],
    "outerjoin": [0, 20],
    "weworkremotely": None,
    "weworkremotely": None,
}

url_selectors = {
    "usajobs": {
        "listings": (
            By.XPATH,
            "//div[@id='usajobs-search-results']/div[@class='usajobs-search-result--core']/a",
        ),
        "next": (By.XPATH, "//a[@title='Go To Next Page']"),
    },
    "progressivedatajobs": {
        "listings": (By.XPATH, "//div[@class='grid-job']/h2/a"),
        "next": ("rel_link", "/job-postings/?wpv_view_count=627&wpv_paged=1"),
    },
    "outerjoin": {
        "listings": (By.XPATH, "//div[@class='w-full ml-4']/a"),
        "next": (By.XPATH, "(//nav/a[@rel='next'])"),
    },
    "weworkremotely": {
        "listings": (By.XPATH, "(//article/ul/li[@class='feature']/a)"),
        "next": (None, None),
    },
}


def get_key(url):
    for key in url_max_pages.keys():
        if re.search(key, url) is not None:
            return key
    raise Exception(url)


class ListingSpider(scrapy.Spider):
    name = "listing"

    def start_requests(self):
        urls = [
            "https://www.usajobs.gov/Search/Results?j=2210&j=1550&j=1560&k=data&p=1",
            #"https://www.progressivedatajobs.org/job-postings/job-postings/?wpv_view_count=627&wpv_paged=1",
            #"https://outerjoin.us/?q=data",
            #"https://weworkremotely.com/categories/remote-back-end-programming-jobs",
            #"https://weworkremotely.com/categories/remote-full-stack-programming-jobs",
        ]

        for url in urls:
            request = self.makeRequest(
                url,
                30,
                self.parsePage,
                url_selectors[get_key(url)]["listings"],
            )
            yield(request)


    def parsePage(self, response):
        
        #inspect_response(response, self)
        driver = response.request.meta["driver"]
        url = driver.current_url
        key = get_key(url)
        next_selector = url_selectors[key]["next"]
        listing_selector = url_selectors[key]["listings"]
        #raise Exception("start")
        #inspect_response(response, self)
        # Get container html elements holding job listing links
        containers = []
        if listing_selector[0] == By.CLASS_NAME:
            containers = response.xpath(f"//div[@class='{listing_selector[1]}']")
        elif listing_selector[0] == By.XPATH:
            containers = response.xpath(listing_selector[1])
        for container in containers:
            rel_link = container.xpath("@href").get()
            end = response.url[8:].index("/") + 8
            if response.url[:end] not in rel_link:
                yield ({"url": response.url[:end] + rel_link})
            else:
                yield ({"url": rel_link})
        #inspect_response(response, self)
        # Stop scraping after n pages
        if url_max_pages[key] is None:
            return
        url_max_pages[key][0] += 1
        if url_max_pages[key][0] >= url_max_pages[key][1]:
            return
        if next_selector[0] == None:
            return
        #inspect_response(response, self)
        # Handle rel links in "/pg=1" format
        if next_selector[0] == "rel_link":
            url = driver.current_url
            end = url.rfind("=") + 1
            index = url[end:]
            if index.isnumeric():
                index = str(int(index) + 1)
            else:
                raise Exception("Unhandled REl link")
            url = driver.current_url[:end] + index

            yield (
                self.makeRequest(
                    url,
                    5,
                    self.parsePage,
                    listing_selector,
                )
            )
            return
        # Handle pages with next buttons
        next = response.xpath(next_selector[1])
        if (
            len(next) == 0
            or next.xpath("@aria-hidden").get() == "true"
            or next.xpath("@display").get() == "none"
        ):
            inspect_response(response, self)
            raise Exception(f"{next}\nNo more pages.")
        # Attempt to get next page n times
        n = 0
        while n < 5:
            try:
                button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(next_selector)
                )
                driver.execute_script(
                    "window.scrollTo(100,document.body.scrollHeight/1.25);"
                )
                time.sleep(1)
                button.click()
                time.sleep(1)
                url = driver.current_url
                yield (
                    self.makeRequest(
                        url,
                        30,
                        self.parsePage,
                        listing_selector,
                    )
                )
            except Exception as e:
                print(f"EXCEPTION: {e}")
                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                n += 1
                continue
            break

    def makeRequest(self, url, tm, cb, listing_selector):
        request = SeleniumRequest(
            url=url,
            wait_time=tm,
            callback=cb,
            wait_until=EC.presence_of_element_located(
                (By.XPATH, f"({listing_selector[1]})[1]")
            ),
        )
        return request
