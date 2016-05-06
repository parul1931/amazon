import urllib2
from bs4 import BeautifulSoup
import urllib
import pytesseract
import Image
import tweepy
from StringIO import StringIO
import requests
from PIL import ImageFilter
import random
import csv
import sys
import logging
from fake_useragent import UserAgent
ua = UserAgent()

product_count = 0

#logger = logging.getLogger("logfile")
logging.basicConfig(filename='example.log',level=logging.DEBUG)


def parse_captcha(link, status):
	if status == 0:
		opener = urllib2.build_opener()
		header = ua.random
		print "\n header : ", header
		print "\n link : ", link
		opener.addheaders = [('User-agent', header)]
		response = opener.open(link)
		data = response.read()
		# code = response.getcode()
		# log = "\n\n\n\n header : {header} \n url : {url} \n response : {response}".format(header=header, url=link, response=code)
		# logging.debug(log)
		#print "log : ", log

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
		 	parse_captcha(link, status)
		else:
	 		status = 1
	 		return
	else:
		return

def links(link):
	opener = urllib2.build_opener()
	header = ua.random
	print "\n header : ", header
	opener.addheaders = [('User-agent', header)]
	response = opener.open(link)
	#code = response.getcode()
	# log = "\n\n\n\n header : {header} \n url : {url} \n response : {response}".format(header=header, url=link, response=code)
	# logging.debug(log)
	# print "log : ", log
	data = response.read()
	soup = BeautifulSoup(data, 'html.parser')

	#status = 0
	#parse_captcha(link, status)

	for li in soup.find_all("li", {"class": "s-result-item  celwidget "}):
		div = li.find("div", {"class": "s-item-container"})
		div1 = div.find("div", {"class": "a-row a-spacing-mini"})
		div2 = div1.find("div", {"class": "a-row a-spacing-none"})
		a = div2.find("a", {"class": "a-link-normal s-access-detail-page  a-text-normal"})
		url = a["href"]
		print "\n\n page link : ", url
		content(url)
	a = soup.find("a", {"id": "pagnNextLink"})
	# if a is None:
	# 	status = 0
	# 	#parse_captcha(link, status)
	# else:
	a = soup.find("a", {"id": "pagnNextLink"})
	link = "http://www.amazon.com"+a["href"]
	print "pagination link : ", link
	links(url)

def content(url):
	# status = 0
	# parse_captcha(link, status)

	opener = urllib2.build_opener()
	header = ua.random
	print "header : ", header
	opener.addheaders = [('User-agent', header)]
	response = opener.open(url)
	data = response.read()
	# code = response.getcode()
	# log = "\n\n\n\n header : {header} \n url : {url} \n response : {response}".format(header=header, url=url, response=code)
	# logging.debug(log)
	# print "log : ", log
	soup_data = BeautifulSoup(data, 'html.parser')

	global product_count
	product_count = product_count+1
	print "product_count : ", product_count

	split_url = url.split("/")
	asin = split_url[5]
	print "asin : ", asin

	new_link = None

	span = soup_data.find("span", {"class": "olp-padding-right"})
	if span:
		a = span.find("a")
		if a:
			if "new" in a.text:
				new_link = "http://www.amazon.com"+a["href"]
				print "new_link : ", new_link
									
	span1 = soup_data.find("span", {"class": "a-size-small aok-float-right"})
	if span1:
		a = span1.find("a")
		if a:
			if "new" in a.text:
				new_link = "http://www.amazon.com"+a["href"]
				print "new_link : ", new_link

	span2 = soup_data.find("span", {"class": "a-size-small"})
	if span2:
		a = span2.find("a")
		if a:
			if "new" in a.text:
				new_link = "http://www.amazon.com"+a["href"]
				print "new_link : ", new_link
								
	span3 = soup_data.find("span", {"class": "a-size-small a-center"})
	if span3:
		a = span3.find("a")
		if a:
			if "new" in a.text:
				new_link = "http://www.amazon.com"+a["href"]
				print "new_link : ", new_link

	span4 = soup_data.find("span", {"class": "olp-new olp-link"})
	if span4:
		a = span4.find("a")
		if a:
			if "new" in a.text:
				new_link = "http://www.amazon.com"+a["href"]
				print "new_link : ", new_link

	if new_link is not None:
		x = 1
		# status = 0
		# parse_captcha(link, status)

		opener = urllib2.build_opener()
		header = ua.random
		print "header : ", header
		opener.addheaders = [('User-agent', header)]
		response = opener.open(new_link)
		data = response.read()
		# code = response.getcode()
		# log = "\n\n\n\n header : {header} \n url : {url} \n response : {response}".format(header=header, url=new_link, response=code)
		# print "log : ", log
		# logging.debug(log)

		price_soup = BeautifulSoup(data, 'html.parser')

		price_list = []

		for div in price_soup.find_all("div", {"class": "a-row a-spacing-mini olpOffer"}):
			div2 = div.find("div", {"class": "a-column a-span3"})
			div3 = div2.find("div", {"class": "a-section a-spacing-small"})
			if "New" in div3.text and x < 3:
				div1 = div.find("div", {"class": "a-column a-span2"})
				span = div1.find("span")
				if span:
					price = ''.join(span.text.split())
					price_list.append(price)
					print "price_list : ", price_list
					x = x+1
		print price_list

		try:
			new_price1 = price_list[0]
			new_price2 = price_list[1]				
			
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
		except Exception as e:
			print "Exception : ", e
		
link = "http://www.amazon.com/s/ref=sr_nr_i_2?srs=3837915031&fst=as%3Aoff&rh=i%3Aspecialty-aps%2Ci%3Agarden&ie=UTF8&qid=1462187384"
links(link)