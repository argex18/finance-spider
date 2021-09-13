import scrapy
from scrapy import Request
from ..items import FinanceSpiderItem
from ..data_format import data


class BBCSpider(scrapy.Spider):
    name = 'bbcspider'
    allowed_domains = ['bbc.com']
    start_urls = ['https://www.bbc.com/news/business/market-data']
    custom_settings = {
        "FILE": "BBCSPIDER.json"
    }

    # def __init__(self, *args):
    # @classmethod
    # def from_crawler(cls, crawler, *args, **kwargs):

    def start_requests(self):
        for start_url in self.start_urls:
            yield Request(start_url, callback=self.parse)

    def parse(self, response, **kwargs):
        currency_symbols = "$€£¥"
        markets = response.css("[role=region]")
        item = FinanceSpiderItem()

        for market in markets:
            for tr in market.xpath("./table/tbody/tr"):
                if market.xpath("descendant::h2[@class='gel-double-pica-bold']/text()").get() == "Markets":  # ok
                    data["markets"].append({
                        "market": tr.xpath(
                            "descendant::a[@class='nw-c-md-overview-table__link']/div/text()"
                            "| descendant::a/span[@class='gs-u-vh']/text()"
                        ).get().replace(' ', '').replace('\n', ''),
                        "link": tr.xpath(
                            "descendant::a/@href"
                        ).get().replace(' ', '').replace('\n', ''),
                        "values": self.__remove_whitespaces(
                            [self.__find_cs(
                                currency_symbols, value
                            ) for value in tr.xpath("descendant::td/div/text()").getall()]
                        )
                    })
                elif market.xpath("descendant::h2[@class='gel-double-pica-bold']/text()").get() == "Currencies":
                    data["currencies"].append({
                        "market": tr.xpath(
                            "descendant::span[@aria-hidden='true']/text()"
                        ).get().replace(' ', '').replace('\n', ''),
                        "link": tr.xpath(
                            "descendant::a/@href"
                        ).get().replace(' ', '').replace('\n', ''),
                        "values": self.__remove_whitespaces(
                            [self.__find_cs(
                                currency_symbols, value
                            ) for value in tr.xpath("descendant::td/div/text()").getall()]
                        )
                    })
                elif market.xpath("descendant::h2[@class='gel-double-pica-bold']/text()").get() == "Commodities":
                    data["commodities"].append({
                        "market": tr.xpath(
                            "descendant::a[@class='nw-c-md-overview-table__link']/div/text()"
                            "| descendant::a/span[@class='gs-u-vh']/text()"
                        ).get().replace(' ', '').replace('\n', ''),
                        "link": tr.xpath(
                            "descendant::a/@href"
                        ).get().replace(' ', '').replace('\n', ''),
                        "values": self.__remove_whitespaces(
                            [self.__find_cs(
                                currency_symbols, value
                            ) for value in tr.xpath("descendant::td/div/text()").getall()]
                        )
                    })

        item["markets"] = data["markets"]
        item["currencies"] = data["currencies"]
        item["commodities"] = data["commodities"]

        return item

    @staticmethod
    def __find_cs(cs: str, string: str) -> str:
        for char in string:
            if char in cs:
                string = string.replace(char, '')
        return string

    @staticmethod
    def __remove_whitespaces(strings: list) -> list:
        for string, n in zip(strings, range(0, len(strings))):
            strings[n] = string.replace(' ', '').replace('\n', '')
        return strings
