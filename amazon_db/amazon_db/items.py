# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AmazonDbItem(scrapy.Item):
	title = scrapy.Field()
	asin = scrapy.Field()
	category = scrapy.Field()
	rank = scrapy.Field()
	new_price1 = scrapy.Field()
	new_price2 = scrapy.Field()


class AmazonProductItem(scrapy.Item):
	asin = scrapy.Field()
	new_price1 = scrapy.Field()
	new_price2 = scrapy.Field()