from scrapy import signals
from scrapy.exporters import CsvItemExporter

class CSVExportPipeline(object):
    counter = 0
    file_count = 1

    def __init__(self):
        self.files = {}

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        if spider.name != '':
            file = open('amazon_products_%s.csv' % (self.file_count),'w+b')
            self.files[spider] = file
            self.export_fields = ['title', 'asin', 'category', 'rank', 'new_price1', 'new_price2']
            self.exporter = CsvItemExporter(file, fields_to_export=self.export_fields)
            self.exporter.start_exporting()

    def spider_closed(self, spider):
        if spider.name != '':
            self.exporter.finish_exporting()
            file = self.files.pop(spider)
            file.close()

    def process_item(self, item, spider):
        if spider.name != '':
            asin = item.get('asin', None)
            if asin:
                self.counter += 1
                if self.counter == 10000:
                    self.exporter.finish_exporting()
                    file = self.files.pop(spider)
                    file.close()

                    self.file_count += 1

                    file = open('amazon_products_%s.csv' % (self.file_count),'w+b')
                    self.files[spider] = file
                    self.export_fields = ['title', 'asin', 'category', 'rank', 'new_price1', 'new_price2']
                    self.exporter = CsvItemExporter(file, fields_to_export=self.export_fields)
                    self.exporter.start_exporting()

                    self.counter = 0
                print self.counter, '*'*50
                self.exporter.export_item(item)
        return item


class AmazonProductsPipeline(object):
    counter = 0

    def process_item(self, item, spider):
        self.counter += 1
        print '\n', self.counter, '*'*50
        return item
