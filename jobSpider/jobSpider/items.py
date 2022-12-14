# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    Title = scrapy.Field()
    Category = scrapy.Field()
    Url = scrapy.Field()
    Type = scrapy.Field()
    Schedule = scrapy.Field()
    Location = scrapy.Field()
    Salary = scrapy.Field()
    Description = scrapy.Field()
    Requirements = scrapy.Field()