# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import pymongo
import scrapy
from scrapy.exporters import JsonItemExporter
from scrapy.utils.python import to_bytes
import json


# https://stackoverflow.com/questions/33290876/how-to-create-custom-scrapy-item-exporter
class FinanceSpiderItemExporter(JsonItemExporter):
    def __init__(self, file, **kwargs):
        super().__init__(file=file, **kwargs)
        self.file = file

    def start_exporting(self):
        self.file = open(self.file, 'wb')
        self.file.write(b"[\n")

    def finish_exporting(self):
        self.file.write(b"\n]")
        self.file.close()

    def export_item(self, item):
        json_data = to_bytes(json.dumps(obj=item, indent=5), encoding='utf-8')
        self.file.write(json_data)


class FinanceSpiderMongoDbItemExporter:
    def __init__(self, db_name: str, collection_name: str, host: str, port: int, user: str = None, pwd: str = None):
        self.db_name = db_name
        self.collection_name = collection_name
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd

        self.client = None
        self.db = None
        self.collection = None

    def start_exporting(self):
        if self.user and self.pwd:
            self.client = pymongo.MongoClient(
                host=self.host, port=self.port, username=self.user, password=self.pwd
            )
        else:
            self.client = pymongo.MongoClient(f"mongodb://{self.host}:{self.port}")
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]

    def finish_exporting(self):
        self.client.close()

    def export_item(self, item):
        try:
            if self.client.is_primary:
                if self.collection.count_documents({}) == 0:
                    for field, n_field in zip(item, range(0, len(item))):
                        self.collection.insert_one({
                            "_id": f"{self.collection_name}_f{n_field}",
                            "name": f"{field}",
                            f"{field}": item[field],
                        })
                else:
                    for field, n_field in zip(item, range(0, len(item))):
                        self.collection.update_one({
                            "_id": f"{self.collection_name}_f{n_field}",
                        }, {
                            "$set": {
                                "name": f"{field}",
                                f"{field}": item[field],
                            }
                        })
            else:
                raise SystemError("Error: the server does not accept writing operations actually")
        except Exception as e:
            for arg in e.args:
                print(arg)


class FinanceSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    markets = scrapy.Field()
    currencies = scrapy.Field()
    commodities = scrapy.Field()
