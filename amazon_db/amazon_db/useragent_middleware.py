import logging
import scrapy
import fake_useragent
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from fake_useragent import UserAgent
ua = UserAgent()

class FakeUserAgentMiddleware(UserAgentMiddleware):
    def __init__(self, user_agent=''):
        self.user_agent = user_agent

    def process_request(self, request, spider):
    	header = ua.random
        if header:
            request.headers.setdefault('User-Agent', header)   
            spider.log(u'User-Agent: {} {}'.format(request.headers.get('User-Agent'), request))