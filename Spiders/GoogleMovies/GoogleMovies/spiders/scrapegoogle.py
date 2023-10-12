import scrapy
import random
from scrapy.selector import Selector
from urllib.parse import urljoin
import re

class ScrapegoogleSpider(scrapy.Spider):
    name = "googlescraper"
    allowed_domains = ["en.wikipedia.org"]
    start_urls = ["https://en.wikipedia.org/wiki/List_of_Walt_Disney_Pictures_films"]
    custom_settings={
        "FEED_FORMAT":"json",
        "FEED_URI":"movies.json"
    }

    user_agent_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.1 Safari/605.1.1',
        'Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
        'Mozilla/5.0 (iPad; CPU OS 15_0_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 Edg/92.0.902.67',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0',
        'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0 Mobile Safari/537.36'

        # Add more user agents as needed
        ]

    def parse(self, response):
        user_agent = random.choice(self.user_agent_list)
        print(f"\n\n\n{user_agent}")
        yield scrapy.Request(url=response.url, headers={'User-Agent': user_agent}, meta={'user_agent': user_agent}, callback=self.parse_page)

    def parse_page(self,response):
        user_agent=response.meta.get("user_agent")
        print(f"\n\n\n{user_agent}")
        tables=response.css("table.wikitable").getall()
        for table in tables:
            table =Selector(text=table)
            links=table.css("tbody tr td i a::attr(href)").getall()
            for link in links:
                # Join the base URL to the link
                absolute_link = urljoin(response.url, link)
                yield scrapy.Request(url=absolute_link, callback=self.get_data)

    def tidy_data(self,content_key,content_value):
        # Filter out unwanted values
        content_value = list(filter(lambda val: val.strip() and "parser" not in val, content_value))
        # Remove unwanted values (empty strings and those containing "parser" or superscript numbers)
        content_value= [re.sub(r'\[\d+\]', '', val).strip() for val in content_value if re.sub(r'\[\d+\]', '', val).strip()]
        if len(content_value) == 1:
            content_value = content_value[0]
        if content_key=="Release dates" or content_key=="Release date":
            content_value=" ".join(content_value).replace("\xa0"," ")
        
        return content_key,content_value

    
    def get_data(self, response):
        table=response.css("table.infobox")
        rows = table.css("tr")
        movie_info={}
        for index,row in enumerate(rows):
            if index==0:
                movie_info["title"]=row.css("::text").get()
            elif index==1:
                continue
            else:
                content_key=row.css("th::text").get()
                if not content_key:
                    content_key=row.css("th div::text").get()
                # Use XPath selector to select text inside <td> excluding <sup> tags
                content_value = row.xpath("td//text()").getall()
                content_key,content_value=self.tidy_data(content_key,content_value)
                if not content_key:
                    continue
                movie_info[content_key]=content_value
        if movie_info:        
            yield movie_info

