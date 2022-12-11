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

"""
 urls = {
            "usajobs": "https://www.usajobs.gov/Search/Results?j=2210&j=1550&j=1560&k=data&p=1",
            #"progressivedatajobs": "https://www.progressivedatajobs.org/job-postings",
            #"outerjoin":"https://outerjoin.us/?q=data",
            #"weworkremotely": "https://weworkremotely.com/categories/remote-back-end-programming-jobs",
            #"weworkremotely": "https://weworkremotely.com/categories/remote-full-stack-programming-jobs"
        }
"""
url_max_pages = {
    "usajobs": [0, 15],
    "progressivedatajobs": [0, 15],
    "outerjoin": [0, 15],
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


class ListingSpider(scrapy.Spider):
    name = "listing"

    def start_requests(self):
        urls = [
            "https://www.usajobs.gov/Search/Results?j=2210&j=1550&j=1560&k=data&p=1",
            # "https://www.progressivedatajobs.org/job-postings",
            # "https://outerjoin.us/?q=data",
            # "https://weworkremotely.com/categories/remote-back-end-programming-jobs",
            # "https://weworkremotely.com/categories/remote-full-stack-programming-jobs",
        ]
        # Selectors for getting next page
        next = [
            (By.XPATH, "//a[@title='Go To Next Page']"),
            ("rel_link", "/job-postings/?wpv_view_count=627&wpv_paged=1"),
            (By.XPATH, "(//nav/a[@rel='next'])"),
            ("na", "na"),
            ("na", "na"),
        ]
        # Selectors for divs containing link to job post
        listing_divs = [
            (
                By.XPATH,
                "//div[@id='usajobs-search-results']/div[@class='usajobs-search-result--core']/a",
            ),
            (By.XPATH, "//div[@class='grid-job']/h2/a"),
            (By.XPATH, "//div[@class='w-full ml-4']/a"),
            (By.XPATH, "(//article/ul/li[@class='feature']/a)"),
            (By.XPATH, "(//article/ul/li[@class='feature']/a)"),
        ]
        requests = [
            self.makeRequest(
                urls[i],
                10,
                self.parsePage,
                # next[i],
                listing_divs[i],
            )
            for i in range(len(urls))
        ]
        return requests

    # , next_selector, listing_selector
    def parsePage(self, response):
        # inspect_response(response, self)
        driver = response.request.meta["driver"]
        url = driver.current_url
        key = ""
        for key_ in url_max_pages.keys():
            if re.search(key_, url) is not None:
                key = key_

        next_selector = url_selectors[key]["next"]
        listing_selector = url_selectors[key]["listings"]
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

        if next_selector[0] == "rel_link":
            #inspect_response(response, self)
            url = (
                driver.current_url
                + next_selector[1][:-1]
                + str(int(next_selector[1][-1]) + 1)
            )
            yield (
                self.makeRequest(
                    url,
                    5,
                    self.parsePage,
                    listing_selector,
                    wait_until=EC.presence_of_element_located(listing_selector),
                )
            )
            return
        # Stop scraping after n pages
        if url_max_pages[key] is None:
            return
        url_max_pages[key][0] += 1
        if url_max_pages[key][0] >= url_max_pages[key][1]:
            return
        if next_selector[0] == None:
            return
        try:
            next = response.xpath(next_selector[1])
        except Exception:
            inspect_response(response, self)
        #inspect_response(response, self)
        if (
            len(next) == 0
            or next.xpath("@aria-hidden").get() == "true"
            or next.xpath("@display").get() == "none"
        ):
            #inspect_response(response, self)
            raise Exception(f"{next}\nNEXT IS NONE!!!!")
            return
        i = 0
        while i < 5:
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
                        5,
                        self.parsePage,
                        listing_selector,
                    )
                )
            except Exception as e:
                print(f"EXCEPTION: {e}")
                # time.sleep(100)
                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                i+=1
                continue
            break

    def makeRequest(self, url, tm, cb, listing_selector):
        request = SeleniumRequest(
            url=url,
            wait_time=tm,
            callback=cb,
            wait_until=EC.presence_of_element_located(listing_selector),
        )
        # request.meta["next_selector"] = next_selector
        # request.meta["listing_selector"] = listing_selector
        # request.cb_kwargs["next_selector"] = next_selector
        # request.cb_kwargs["listing_selector"] = listing_selector
        return request
