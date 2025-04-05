# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.http import Request
from scrapy.spiders import Spider

from dotenv import load_dotenv

import os


class ProxyMiddleware:
    # ProxyMiddleware. Important since the website has geo-blocking

    def __init__(self):
        load_dotenv()
        self.proxy = os.getenv("PROXY")
        self.use_proxy = bool(self.proxy)

    
    @classmethod
    def from_crawler(cls, crawler):
        return cls()
    

    def process_request(self, request: Request, spider: Spider):
        if self.use_proxy:
            request.meta['proxy'] = self.proxy
            spider.logger.info(f"Using proxy: {self.proxy}")

        else:
            spider.logger.info("No proxy configured")