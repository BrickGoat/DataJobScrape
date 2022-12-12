import scrapy
import time
import re
from selenium.webdriver.common.action_chains import ActionChains
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
import pandas as pd
from ..items import JobspiderItem

def makeSelector(title, cat, type, schedule, location, salary, desc, req=None):
    return {
        "Title": title,
        "Category": cat,  # site specific job cat
        "Type": type,  # Permanant/ not permanant
        "Schedule": schedule,  # full time / part time
        "Location": location,
        "Salary": salary,  # base salary
        "Description": desc,  # topic model on & potentially parse out other columns
        "Requirements": req,  # Req/Duties topic model on & parse out yrs of exp & languages
        # "Experience": exp,
    }


class JobsSpider(scrapy.Spider):
    name = "job"

    def start_requests(self):
        urls = pd.read_json(
            "/home/brick/Documents/jobsScrape/DataJobScrape/jobSpider/urls_all.jl",
            lines=True,
        )
        urls = urls.iloc[0:, 0]
        selectors = {
            "usajobs": makeSelector(
                "//div/h1[@id='job-title']",
                "//h5/span[contains(text(), 'Job family (Series)')]/parent::h5/following-sibling::p",
                "//h5/span[contains(text(), 'Appointment type')]/parent::h5/following-sibling::p",
                "//h5/span[contains(text(), 'Work schedule')]/parent::h5/following-sibling::p",
                "//span[@class='usajobs-joa-locations__city']",
                "//span[@itemprop='baseSalary']",
                "//h2[contains(text(), 'Summary')]/following-sibling::div/p",
                "//div[@id='duties']",
            ),
            "progressivedatajobs": makeSelector(
                "//h1/span",
                "//h3[contains(text(), 'Job Role')]/following-sibling::p",
                "(//div[@class='uabb-subheading uabb-text-editor']/p)[1]",
                None,
                "//h3[contains(text(), 'Salary Range')]/preceding-sibling:p",
                "//h3[contains(text(), 'Salary Range')]/following-sibling:p",
                "//div[@class='fl-rich-text']",
                "//div[@class='fl-rich-text']/ul/li",
            ),
            "outerjoin": makeSelector(
                "(//h1)[1]",
                None,
                None,
                None,
                None,
                None,
                "(//div[@class='job-description'])[1]/article",
            ),
            "weworkremotely": makeSelector(
                "(//div[@class='listing-header-container'])[1]/h1",
                "(//div[@class='listing-header-container'])[1]/br/following-sibling:a",
                None,
                "(//div[@class='listing-header-container'])[1]/br/following-sibling:a",
                "((//div[@class='company-card'])[1]/h3)[1]",
                None,
                "//div[@id='job-listing-show-container']",
                "//div[@id='job-listing-show-container']/ul/li",
            ),
        }

        requests = []
        for url in urls:
            for selector in selectors.keys():
                if re.search(selector, url) is not None:
                    request = self.makeRequest(
                        url, 10, self.parsePage, selectors[selector]
                    )
                    requests.append(request)
        return requests

    def parsePage(self, response, selectors):
        #from scrapy.shell import inspect_response
        #inspect_response(response, self)
        url = response.url
        time.sleep(1)
        item = JobspiderItem()
        item["Url"] = url
        for selector in selectors.keys():
            elements = response.xpath(f"({selectors[selector]})")
            for ele in elements:
                data = ele.xpath(".//text()").extract()
                if len(data) != 0:
                    data = "".join(data).strip()
                    break

            if len(data) > 0:
                item[selector] = data
            else:
                item[selector] = None
        return item


    def makeRequest(self, url, tm, cb, selectors):
        request = SeleniumRequest(
            url=url,
            wait_time=tm,
            callback=cb,
            wait_until=EC.presence_of_element_located(
                (By.XPATH, selectors["Description"])
            ),
        )
        request.cb_kwargs["selectors"] = selectors
        return request
