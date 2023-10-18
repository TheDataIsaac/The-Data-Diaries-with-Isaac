import scrapy
import random
from urllib.parse import urlencode
from scraper_params import user_agents, initial_params, pagination_params, headers
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector

class GoogleScraper(scrapy.Spider):
    name = "searchscraper"
    query="digital marketing"
    user_agents = user_agents
    pagination_params = pagination_params
    initial_params = initial_params
    custom_headers = headers
    pages=5
    scraped_data=[]
    custom_settings = {
        "FEEDS": {
            "searchresult.json": {"format": "json"}
        },
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "DOWNLOAD_DELAY": 2
        }

    def start_requests(self):
        for page in range(0, int(self.pages)):
            self.custom_headers["user-agent"] = random.choice(self.user_agents)
            '''Makes HTTP GET request to fetch search results from google'''
            self.initial_params['q'] = self.query

            if not page:
                custom_params = self.initial_params
            else:
                custom_params = self.pagination_params
                custom_params['start'] = str(page * 10)
                custom_params['q'] = self.query

            base_url = "https://www.google.com/search?"
            base_url=base_url+urlencode(custom_params)
            print("\n\n\n",page)
            yield scrapy.Request(url=base_url, headers=self.custom_headers, meta={'user_agent': self.custom_headers["user-agent"]}, callback=self.parse_page)

        
    def parse_page(self,response):
        user_agent=response.meta.get("user_agent")
        print(f"\n\n\n{user_agent}")
        print("\n\n",response.url)
        response=response.text
        response=Selector(text=response)

        data = response.css("a[jsname='UWckNb']")
        for datum in data:
            title=datum.css("::text").get()
            link=datum.css("::attr(href)").get()
            if link not in self.scraped_data:
                self.scraped_data.append({title:link})
                yield {title:link}

        

        
if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(GoogleScraper)
    process.start()


