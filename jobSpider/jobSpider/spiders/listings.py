import scrapy
from scrapy_selenium import SeleniumRequest

class ListingSpider(scrapy.Spider):
    name="listing"

    def start_requests(self):
        urls = [
            "https://www.usajobs.gov/Search/Results?k=data",
            "https://datajobs.com/Data-Jobs~1",
            "https://www.progressivedatajobs.org/job-postings/",
            "https://outerjoin.us/?q=data",
            "https://weworkremotely.com/categories/remote-back-end-programming-jobs",
            "https://weworkremotely.com/categories/remote-full-stack-programming-jobs"
        ]
        return [SeleniumRequest(
            url=url,
            wait_time=3,
            callback=self.parse
        ) for url in urls]

    def parse(self, response):
        pass
