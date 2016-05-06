import scrapy
from bs4 import BeautifulSoup
import urllib
import urllib2
import pytesseract
from amazon_db.items import AmazonProductItem
import Image
import tweepy
from StringIO import StringIO
import requests
import sys
from PIL import ImageFilter
import random
from fake_useragent import UserAgent
ua = UserAgent()

product_count = 0

class ElectronicSpider(scrapy.Spider):
	name = "test"
	allowed_domains = ["amazon.com"]
	start_urls = ["http://www.amazon.com/s/ref=sr_nr_i_0?srs=3837915031&fst=as%3Aoff&rh=i%3Aspecialty-aps%2Ci%3Aelectronics&ie=UTF8&qid=1462161300"]

	def start_requests(self):
		header = ua.random
		headers = {"Accept": "*/*", "Accept-Encoding": "gzip, deflate", "User-Agent": header}
		yield scrapy.Request(url=self.start_urls[0], headers=headers, callback=self.parse_data)

		for i in range(2,401):
			url = "http://www.amazon.com/s/ref=sr_pg_{i}?srs=3837915031&fst=as%3Aoff&rh=n%3A172282&page={i}&ie=UTF8&qid=1462340464".format(i=i)
			header = ua.random
			headers = {"Accept": "*/*", "Accept-Encoding": "gzip, deflate", "User-Agent": header}
			yield scrapy.Request(url, headers=headers, callback=self.parse_data)


	def parse_data(self, response):
		html = response.body
		soup = BeautifulSoup(html, 'html.parser')
		link = response.url

		div = soup.find("div", {"class": "a-row a-text-center"})
		if div:
			status = 0
			self.parse_captcha(link, status)
		
		i = 1

		for li in soup.find_all("li", {"class": "s-result-item  celwidget "}):
			div = li.find("div", {"class": "s-item-container"})
			div1 = div.find("div", {"class": "a-row a-spacing-mini"})
			div2 = div1.find("div", {"class": "a-row a-spacing-none"})
			a = div2.find("a", {"class": "a-link-normal s-access-detail-page  a-text-normal"})
			url = a["href"]
			print "\n", "page link ", i, "  : ", url
			split_url = url.split("/") 
			asin = split_url[5]
			new_link = "http://www.amazon.com/gp/offer-listing/"+asin+"/ref=dp_olp_all_mbc?ie=UTF8&condition=all"
			header = ua.random
			headers = {"Accept": "*/*", "Accept-Encoding": "gzip, deflate", "User-Agent": header}
			yield scrapy.Request(new_link, headers=headers, meta={'asin': asin}, callback=self.parse_content)
			i = i+1

	def parse_content(self, response):
		asin = response.meta['asin']
		html1 = response.body
		soup_data = BeautifulSoup(html1, 'html.parser')

		global product_count
		product_count = product_count+1
		print "\n\n product_count : ", product_count
		print "asin : ", asin

		price_list = []
		item = AmazonProductItem()

		item["asin"] = asin

		div = soup_data.find("div", {"class": "a-row a-text-center"})
		if div:
			status = 0
			self.parse_captcha(link, status)

		x = 1

		for div in soup_data.find_all("div", {"class": "a-row a-spacing-mini olpOffer"}):
			div2 = div.find("div", {"class": "a-column a-span3"})
			div3 = div2.find("div", {"class": "a-section a-spacing-small"})
			if "New" in div3.text and x < 3:
				div1 = div.find("div", {"class": "a-column a-span2"})
				span = div1.find("span")
				if span:
					price = ''.join(span.text.split())
					price_list.append(price)
					print "\n\n price_list : ", price_list
					x = x+1
		print price_list

		try:
			new_price1 = price_list[0]
			new_price2 = price_list[1]				
			item["new_price1"] = new_price1
			item["new_price2"] = new_price2
			
			price1 = float(new_price1.split("$")[1])
			print "price1 : ", price1
			price2 = float(new_price2.split("$")[1])
			print "price2 : ", price2

			price = price2 / price1
			print "price : ", price

			if price > 2:
				auth = tweepy.OAuthHandler("0kFCrizKx4UFzFGfVKCZdJIFS", "d9eRNNVdDHy067VweYKbpEbei8gQicRQwMpGUSFFop0XimthCL")
				auth.set_access_token("213512945-94181AvMplNNqoDXxO7z1uOqPDEIiAMehivblXdo", "253adDmTAFS6WdwKUBzVnPoV0Iq9dPsOBiWGgAKdlaNid")
				api = tweepy.API(auth)
				tweet = "asin : "+asin
				print "\n\n tweet : ", tweet
				status = api.update_status(status=tweet) 
				print "status : ", status
			yield item
		except Exception as e:
			print "Exception : ", e

	def parse_captcha(self, link, status):
		try:
			if status == 0:
				#proxies = ['http://43.242.104.43', 'http://115.113.43.215', 'http://115.113.43.215']
				#proxy = random.choice(proxies)
				proxy = urllib2.ProxyHandler({'http': 'http://14.142.4.33'})
				opener = urllib2.build_opener()
				header = ua.random
				print "\n header : ", header
				print "\n link : ", link
				opener.addheaders = [('User-agent', header)]
				data = opener.open(link).read()

				soup = BeautifulSoup(data, 'html.parser')
				div1 = soup.find("div", {"class": "a-row a-text-center"})
				if div1 is not None:
					print "\n\n status in captcha : ", status
					print "\n link in captcha : ", link
					img = div1.find("img")
				 	image = img["src"]
				 	print "\n captcha.."
				 	print "image : ", image
				 	image = Image.open(StringIO(requests.get(image).content))
					image.filter(ImageFilter.SHARPEN)
					captcha = pytesseract.image_to_string(image)
					print "captcha : ", captcha
				 	values = {'field-keywords' : captcha}
				 	data = urllib.urlencode(values)
				 	req = urllib2.Request(link, data, {'User-agent': header})
				 	resp = urllib2.urlopen(req)
				 	the_page = resp.read()
				 	self.parse_captcha(link, status)
				else:
			 		status = 1
			 		return
		except Exception as e:
			print "\n Exception : ", e