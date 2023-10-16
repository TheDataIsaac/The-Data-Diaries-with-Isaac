from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class EtsyJewelry(CrawlSpider):
    name = "etsyscraper"
    allowed_domains = ["etsy.com"]
    start_urls = ["https://www.etsy.com/search?q=handmade+jewelry"]

    rules = (
        # Rule to follow listing links
        Rule(LinkExtractor(allow=r'/listing/'), callback='parse_item'),
        # Rule to follow pagination links
        Rule(LinkExtractor(allow=r'search\?q=handmade\+jewelry.*page=\d+'), follow=True),
    )


    def parse_item(self, response):
        title=response.css("h1[class='wt-text-body-01 wt-line-height-tight wt-break-word wt-mt-xs-1']::text").get().strip()
        brand=response.css("span[class='wt-text-title-small'] a::text").get().strip()
        try:
            price=response.css("p[class='wt-text-title-largest wt-mr-xs-1 wt-text-slime'] *::text").getall()[-1].strip()
        except:
            try:
                price=response.css("p[class='wt-text-title-largest wt-mr-xs-1 '] *::text").getall()[-1].strip()
            except:
                price=""
                                         
        yield {
            "title":title,
            "brand":brand,
            "price":price
        }




# Run the spider
if __name__ == "__main__":
    process = CrawlerProcess({
        "FEEDS": {
            "jewelry.json": {
                "format": "json",
                "overwrite": True
            }
        }
    })
    process.crawl(EtsyJewelry)
    process.start()