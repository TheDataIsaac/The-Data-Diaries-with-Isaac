# https://nitter.net/search?f-tweets&q=from%3A%40{username}&f-images=on&e-nativeretwets=on&e-replies=on


import scrapy
import random
import requests
from urllib.parse import urljoin
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector

class TwitterMediaSpider(scrapy.Spider):
    name = "mediascraper"
    username = "IsaacMustTalk"
    start_urls = [f"https://nitter.net/search?f-tweets&q=from%3A%40{username}&f-images=on&e-nativeretweets=on&e-replies=on"]
    user_agent=''

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
        yield scrapy.Request(url=response.url, headers={'User-Agent': user_agent}, meta={'user_agent': user_agent}, callback=self.get_data)



    def get_data(self,response):
        user_agent=response.meta.get('user_agent')   
        video_elements=response.css("div[class='attachment image']")
        for video_element in video_elements:
            image_url = urljoin("https://nitter.net/", video_element.css(" a::attr(href)").get())
            yield {"image_url":image_url}
            self.save_image(image_url)


    def save_image(self,image_url):
        img_name = image_url.split("/")[-1]  # Extracts the name of the image from its URL
        with open(img_name, "wb") as img_file:
            headers = {"User-Agent": random.choice(self.user_agent_list)}
            print("\n\n\n",headers["User-Agent"])
            img_data = requests.get(image_url,headers=headers).content
            img_file.write(img_data)





if __name__=="__main__":
    process=CrawlerProcess()
    process.crawl(TwitterMediaSpider)
    process.start()




