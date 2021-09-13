# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import json
from .items import FinanceSpiderItemExporter, FinanceSpiderMongoDbItemExporter


DB_NAME = "financespider"  # name of the database


def serialize_to_json(item: dict) -> str:
    return json.dumps(obj=item, indent=5)


class FinanceSpiderPipeline(object):
    def __init__(self, file, exporter, spider):
        self.file = file
        self.exporter = exporter
        self.spider = spider

    @classmethod
    def from_crawler(cls, crawler):
        cls.file = crawler.spider.custom_settings["FILE"]  # exists?
        cls.exporter = FinanceSpiderItemExporter(cls.file)
        cls.spider = crawler.spider
        return cls(
            cls.file,
            cls.exporter,
            cls.spider
        )

    def open_spider(self, spider):
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(ItemAdapter(item).asdict())
        return item


class FinanceSpiderMongoDbPipeline(object):
    def __init__(self, exporter, spider):
        self.exporter = exporter
        self.spider = spider

    @classmethod
    def from_crawler(cls, crawler):
        mongo_settings = crawler.settings.get("MONGO_DB")[DB_NAME]
        db_name = DB_NAME
        cn = crawler.spider.name
        host = mongo_settings["host"]
        port = mongo_settings["port"]
        user = mongo_settings["user"]
        pwd = mongo_settings["pwd"]

        cls.exporter = FinanceSpiderMongoDbItemExporter(db_name, cn, host, port, user, pwd)
        cls.spider = crawler.spider
        return cls(cls.exporter, cls.spider)

    def open_spider(self, spider):
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(ItemAdapter(item).asdict())
        return item
