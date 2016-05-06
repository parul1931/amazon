import scrapy
from bs4 import BeautifulSoup
import sys
import requests
from scrapy.utils.response import open_in_browser
from scrapy.http import FormRequest
import urllib2
import urllib
import Image
from scrapy.spiders import CrawlSpider
import tweepy
#from scrapy.loader import ItemLoader
import pytesseract
from scrapy.http import HtmlResponse
from amazon_db.items import AmazonDbItem
from fake_useragent import UserAgent
ua = UserAgent()


class CategorySpider(scrapy.Spider):
	name = "amazon"
	allowed_domains = ["amazon.com"]
	start_urls = ["http://www.amazon.com/All-Categories/s?ie=UTF8&page=1&rh=i%3Aspecialty-aps&srs=3837915031"]

	def parse(self, response):
		html = response.body
		soup = BeautifulSoup(html, 'html.parser')

		div = soup.find("div", {"class": "categoryRefinementsSection"})

		count = 1
		src=''
		ie=''
		rh=''
		rh1=''
		rh2=''
		for ul in div.find_all("ul"):
			for li in ul.find_all("li"):
				a = li.find("a")
				if "Departments" not in a.text:
					splithref = a["href"].split("srs=")
					src=splithref[1]
					splithref = a["href"].split("&page=")
					splithref = splithref[0]
					splithref = splithref.split("ie=")
					ie=splithref[1]
					splithref = a["href"].split("&srs=")
					splithref = splithref[0]
					splithref = splithref.split("rh=")
					rh=splithref[1]
					splithref = rh.split("%2C")
					rh1 = splithref[0]
					rh2 = splithref[1]
					print "\n\n rh1 : ", rh1
					link='http://www.amazon.com/s/ref=sr_nr_i_0?srs='+src+'&fst=as%3Aoff&rh='+rh2+'%2C'+rh1+'&ie='+ie+'&qid=1461746219'
					print "category link : ", link
					#self.pagination(link)
					yield scrapy.Request("http://www.amazon.com", meta={'link': link}, callback=self.pagination)

	def pagination(self, response): 
		link = response.meta['link']
		print "pagination link : ", link
		for i in range(100):
			opener = urllib2.build_opener()
			header = ua.random
			#headers = {"User-Agent": header}
			opener.addheaders = [('User-agent', header)]
			data = opener.open(link).read()
			# # header = ua.random
			# # headers = {"User-Agent": header}
			# # r = requests.get(link, headers=headers)
			# data = r.text
			# print "\n status : ", r.status_code
			soup1 = BeautifulSoup(data, 'html.parser')
			div1 = soup1.find("div", {"class": "a-row a-text-center"})
			if div1:
				img = div1.find("img")
				image = img["src"]
				img_name = image.split("/")[-1]
				print "\n captcha in pagination ..."
				print "img_name : ", img_name
				print "image : ", image
				resource = urllib.urlopen(image)
				output = open(img_name,"wb")
				output.write(resource.read())
				output.close()
				captcha = pytesseract.image_to_string(Image.open(img_name)) 
				print "captcha : ", captcha
				values = {'field-keywords' : captcha}
				data = urllib.urlencode(values)
				req = urllib2.Request(link, data, {'User-agent': 'Mozilla/5.0'})
				resp = urllib2.urlopen(req)
				the_page = resp.read()
			else:
				#self.product_link(link)
				print "sending Request to product_link"
				print "link : ", link
				yield scrapy.Request("http://www.amazon.com/BESTEK-Portable-International-Adapter-Converter/dp/B012ERZ7B8/ref=sr_1_2377?s=electronics&ie=UTF8&qid=1461918761&sr=1-2377", meta={'link': link}, callback=self.product_link)
				a = soup1.find("a", {"id": "pagnNextLink"})
				link = "http://www.amazon.com"+a["href"]
				print "next link : ", link
				#self.pagination(link)
				yield scrapy.Request("http://www.amazon.com/BESTEK-Portable-International-Adapter-Converter/dp/B012ERZ7B8/ref=sr_1_2377?s=electronics&ie=UTF8&qid=1461918761&sr=1-2377", meta={'link': link}, callback=self.pagination)
				#yield scrapy.Request(link, callback=self.product_link)
				

	def product_link(self, response):
		link = response.meta['link']
		#link = response.url
		print "product link : ", link
		for i in range(100):
			# header = ua.random
			# headers = {"User-Agent": header}
			# r = requests.get(link, headers=headers)
			# hdata = r.text
			# print "\n status : ", r.status_code
			opener = urllib2.build_opener()
			header = ua.random
			opener.addheaders = [('User-agent', header)]
			hdata = opener.open(link).read()
			soup2 = BeautifulSoup(hdata, 'html.parser')
			div1 = soup2.find("div", {"class": "a-row a-text-center"})
			if div1:
				img = div1.find("img")
		 		image = img["src"]
		 		img_name = image.split("/")[-1]
		 		print "\n captcha in product_link .."
		 		print "img_name : ", img_name
		 		print "image : ", image
		 		resource = urllib.urlopen(image)
		 		output = open(img_name,"wb")
		 		output.write(resource.read())
		 		output.close()
		 		captcha = pytesseract.image_to_string(Image.open(img_name)) 
		 		print "captcha : ", captcha
		 		values = {'field-keywords' : captcha}
		 		data = urllib.urlencode(values)
		 		req = urllib2.Request(link, data, {'User-agent': 'Mozilla/5.0'})
		 		resp = urllib2.urlopen(req)
		 		the_page = resp.read()
		 	else:
		 		#ul = soup2.find("ul", {"id": "s-results-list-atf"})
		 		for li in soup2.find_all("li", {"class": "s-result-item  celwidget "}):
		 			div = li.find("div", {"class": "s-item-container"})
		 			div1 = div.find("div", {"class": "a-row a-spacing-mini"})
		 			div2 = div1.find("div", {"class": "a-row a-spacing-none"})
		 			#div3 = div2.find("div", {"class": "a-section a-spacing-none a-inline-block s-position-relative"})
		 			a = div2.find("a", {"class": "a-link-normal s-access-detail-page  a-text-normal"})
		 			url = a["href"]
		 			print "url : ", url
		 			#self.product_content(url)
		 			#yield scrapy.Request("http://www.amazon.com/BESTEK-Portable-International-Adapter-Converter/dp/B012ERZ7B8/ref=sr_1_2377?s=electronics&ie=UTF8&qid=1461918761&sr=1-2377", meta={'url': url}, callback=self.product_content)
		 			yield scrapy.Request(url, callback=self.product_content)
		 		break

	def product_content(self, response):
		#url = response.meta['url']
		url = response.url
		print "\n\n link for product content : ", url
		for i in range(100):
		# 	header = ua.random
		# 	headers = {"User-Agent": header}
		# 	r = requests.get(link, headers=headers)
		# 	html_data = r.text
		# 	print "\n status : ", r.status_code
			opener = urllib2.build_opener()
			header = ua.random
			#headers = {"User-Agent": header}
			opener.addheaders = [('User-agent', header)]
			html_data = opener.open(url).read()
			soup_data = BeautifulSoup(html_data, 'html.parser')
			div1 = soup_data.find("div", {"class": "a-row a-text-center"})
			if div1:
				img = div1.find("img")
				image = img["src"]
				img_name = image.split("/")[-1]
				print "\n captcha in product content ..."
				print "img_name : ", img_name
				print "image : ", image
				resource = urllib.urlopen(image)
				output = open(img_name,"wb")
				output.write(resource.read())
				output.close()
				captcha = pytesseract.image_to_string(Image.open(img_name)) 
				print "captcha : ", captcha
				values = {'field-keywords' : captcha}
				data = urllib.urlencode(values)
				req = urllib2.Request(url, data, {'User-agent': 'Mozilla/5.0'})
				resp = urllib2.urlopen(req)
				the_page = resp.read()
			else:
				print "\n link in product_content : ", url

				item = AmazonDbItem()

				new_link = None
				rank = ''

				title1 = soup_data.find("span", {"id": "productTitle"})
				if title1:
					title = ' '.join(title1.text.split())

				title2 = soup_data.find("span", {"id": "title"})
				if title2:
					title = ' '.join(title2.text.split())

				h1 = soup_data.find("h1", {"class": "a-size-large a-spacing-none"})
				if h1:
					title = ' '.join(h1.text.split())

				split_url = url.split("/")
				asin = split_url[5]
				asin = asin

				category = soup_data.find("span", {"class": "nav-a-content"}).text
				category = category

				li = soup_data.find("li", {"id": "SalesRank"})
				if li:
					list = li.text.split()
					for j in range(len(list)):
						if "#" in list[j]:
							rank = list[j]
							break
				for div in soup_data.find_all("div", {"class": "a-section table-padding"}):
					table = div.find("table", {"id": "productDetails_detailBullets_sections1"})
					if table:
						for tr in table.find_all("tr"):
							if "Rank" in tr.text:
								td = tr.find("td")
								list = td.text.split()
								for j in range(len(list)):
									if "#" in list[j]:
										rank = list[j]
										break
								break
						break

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
					for i in range(100):
						# header = ua.random
						# headers = {"User-Agent": header}
						# r = requests.get(link, headers=headers)
						# price_data = r.text
						# print "\n status : ", r.status_code
						opener = urllib2.build_opener()
						header = ua.random
						#headers = {"User-Agent": header}
						opener.addheaders = [('User-agent', header)]
						price_data = opener.open(new_link).read()
						price_soup = BeautifulSoup(price_data, 'html.parser')
						div1 = price_soup.find("div", {"class": "a-row a-text-center"})
						if div1:
							img = div1.find("img")
							image = img["src"]
							img_name = image.split("/")[-1]
							print "\n captcha in pagination ..."
							print "img_name : ", img_name
							print "image : ", image
							resource = urllib.urlopen(image)
							output = open(img_name,"wb")
							output.write(resource.read())
							output.close()
							captcha = pytesseract.image_to_string(Image.open(img_name)) 
							print "captcha : ", captcha
							values = {'field-keywords' : captcha}
							data = urllib.urlencode(values)
							req = urllib2.Request(new_link, data, {'User-agent': 'Mozilla/5.0'})
							resp = urllib2.urlopen(req)
							the_page = resp.read()
						else:
							x = 1

							for div in price_soup.find_all("div", {"class": "a-row a-spacing-mini olpOffer"}):
								div2 = div.find("div", {"class": "a-column a-span3"})
								div3 = div2.find("div", {"class": "a-section a-spacing-small"})
								if "New" in div3.text and x < 3:
									div1 = div.find("div", {"class": "a-column a-span2"})
									span = div1.find("span")
									price = ''.join(span.text.split())
									price_list.append(price)
									x = x+1
							print price_list
							
							item["title"] = title
							print "title : ", item["title"]
							item["asin"] = asin
							print "asin : ", item["asin"]
							item["rank"] = rank
							print "rank : ", item["rank"]
							item["category"] = category
							print "category : ", item["category"]
							
							try:
								new_price1 = price_list[0]
								new_price2 = price_list[1]
							
								item["new_price1"] = new_price1
								print "new_price1 : ", new_price1
								item["new_price2"] = new_price2
								print "new_price2 : ", new_price2

								price1 = float(new_price1.split("$")[1])
								print "price1 : ", price1
								price2 = float(new_price2.split("$")[1])
								print "price2 : ", price2

								price = price2 / price1
								print "price : ", price

								if price > 2:
									#self.tweet(asin)
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
							break
				break



	# def get_api(self):
	# 	#auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
	# 	#auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
	# 	auth = tweepy.OAuthHandler("0kFCrizKx4UFzFGfVKCZdJIFS", "d9eRNNVdDHy067VweYKbpEbei8gQicRQwMpGUSFFop0XimthCL")
	# 	auth.set_access_token("213512945-94181AvMplNNqoDXxO7z1uOqPDEIiAMehivblXdo", "253adDmTAFS6WdwKUBzVnPoV0Iq9dPsOBiWGgAKdlaNid")
	# 	return tweepy.API(auth)

	# def tweet(self, asin):
	# 	#cfg = {"consumer_key": "0kFCrizKx4UFzFGfVKCZdJIFS", "consumer_secret": "d9eRNNVdDHy067VweYKbpEbei8gQicRQwMpGUSFFop0XimthCL", "access_token": "213512945-94181AvMplNNqoDXxO7z1uOqPDEIiAMehivblXdo", "access_token_secret": "253adDmTAFS6WdwKUBzVnPoV0Iq9dPsOBiWGgAKdlaNid"}
	# 	api = self.get_api()
	# 	tweet = "asin : "+asin
	# 	print "\n\n tweet"
	# 	status = api.update_status(status=tweet) 
	# 	print "status : ", status
    