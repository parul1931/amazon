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


class CellPhoneSpider(scrapy.Spider):
	name = "cell_phones_and_accessories"
	allowed_domains = ["amazon.com"]
	start_urls = ["http://www.amazon.com/s/ref=sr_nr_i_1?srs=3837915031&fst=as%3Aoff&rh=i%3Aspecialty-aps%2Ci%3Amobile&ie=UTF8&qid=1462187384"]

	def parse(self, response):
		print "\n\n response url : ", response.url
		print "response status : ", response.status
		print "response.headers : ", response.headers
		html = response.body
		soup = BeautifulSoup(html, 'html.parser')
		link = response.url

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
			header = ua.random
			yield scrapy.Request(url, headers={"User-agent": header}, callback=self.parse_content)
					 	
			i = i+1

		a = soup.find("a", {"id": "pagnNextLink"})
		if a is None:
			status = 0
			self.parse_captcha(link, status)
		else:
			a = soup.find("a", {"id": "pagnNextLink"})
			link = "http://www.amazon.com"+a["href"]
			print "pagination link : ", link
			header = ua.random
			yield scrapy.Request(link, headers={"User-agent": header}, callback=self.parse)

	def parse_content(self, response):
		print "\n\n response url : ", response.url
		print "response status : ", response.status
		print "response.headers : ", response.headers
		html1 = response.body
		soup_data = BeautifulSoup(html1, 'html.parser')

		url = response.url

		global product_count
		product_count = product_count+1
		print "\n\n product_count : ", product_count

		status = 0
		link = url
		self.parse_captcha(link, status)	
		
		item = AmazonProductItem()
		new_link = None

		split_url = url.split("/")
		asin = split_url[5]
		asin = asin
		print "asin : ", asin

		span = soup_data.find("span", {"class": "olp-padding-right"})
		if span:
			a = span.find("a")
			if a:
				if "new" in a.text:
					new_link = "http://www.amazon.com"+a["href"]
								
		span1 = soup_data.find("span", {"class": "a-size-small aok-float-right"})
		if span1:
			a = span1.find("a")
			if a:
				if "new" in a.text:
					new_link = "http://www.amazon.com"+a["href"]

		span2 = soup_data.find("span", {"class": "a-size-small"})
		if span2:
			a = span2.find("a")
			if a:
				if "new" in a.text:
					new_link = "http://www.amazon.com"+a["href"]
									
		span3 = soup_data.find("span", {"class": "a-size-small a-center"})
		if span3:
			a = span3.find("a")
			if a:
				if "new" in a.text:
					new_link = "http://www.amazon.com"+a["href"]
									
		span4 = soup_data.find("span", {"class": "olp-new olp-link"})
		if span4:
			a = span4.find("a")
			if a:
				if "new" in a.text:
					new_link = "http://www.amazon.com"+a["href"]

		price_list = []
									
		if new_link is not None:
			link = new_link
			self.parse_captcha(link, status)	
			x = 1
			opener = urllib2.build_opener()
			header = ua.random
			print "\n header : ", header
			opener.addheaders = [('User-agent', header)]
			data = opener.open(link).read()
			price_soup = BeautifulSoup(data, 'html.parser')

			for div in price_soup.find_all("div", {"class": "a-row a-spacing-mini olpOffer"}):
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

			item["asin"] = asin
								
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
		print "\n\n status in captcha : ", status
		print "\n link in captcha : ", link
		try:
			if status == 0:
				#proxies = ['http://43.242.104.43', 'http://115.113.43.215', 'http://115.113.43.215']
				#proxy = random.choice(proxies)
				#proxy = urllib2.ProxyHandler({'http': 'http://115.113.43.215'})
				opener = urllib2.build_opener()
				header = ua.random
				print "\n header : ", header
				print "\n link : ", link
				opener.addheaders = [('User-agent', header)]
				data = opener.open(link).read()

				soup = BeautifulSoup(data, 'html.parser')
				div1 = soup.find("div", {"class": "a-row a-text-center"})
				if div1 is not None:
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
