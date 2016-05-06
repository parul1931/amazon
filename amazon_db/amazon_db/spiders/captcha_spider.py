import scrapy

class CaptchaSpider(scrapy.Spider):
	name = "captcha"
	start_urls = ["http://www.amazon.com/s/ref=sr_nr_i_0?srs=3837915031&fst=as%3Aoff&rh=i%3Aspecialty-aps%2Ci%3Aelectronics&ie=UTF8&qid=1461746219"]

	def parse(self, response):
		url = response.url
		print "\n\n url : ", url