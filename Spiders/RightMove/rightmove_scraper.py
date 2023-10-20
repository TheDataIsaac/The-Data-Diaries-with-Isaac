import scrapy
import random
import json
from urllib.parse import urlencode
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector

class RightMoveScraper(scrapy.Spider):
    name = "rightmove"
    base_url="https://www.rightmove.co.uk/property-to-rent/find.html?"
    page_num=1
    postal_code_index=0
    postal_codes = ["CR0", "AB10", "B9", "M1", "L1", "E1", "W1", "SW1", "N1", "NW1",
                    "SE1", "WC1", "EC1", "RH1", "GU1", "BN1", "TN1", "ME1", "CT1", "DA1",
                    "BR1", "RM1", "IG1", "EN1", "WD1", "HA1", "UB1", "TW1", "KT1", "SM1",
                    "SL1", "RG1", "SN1", "SP1", "SO1", "PO1", "BH1", "DT1", "TA1", "EX1",
                    "TQ1", "PL1", "TR1", "BA1", "BS1", "GL1", "CF1", "NP1", "HR1", "LD1"]
    
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

    custom_settings = {
        "FEEDS": {
            "properties.json": {"format": "json"}
        },
        #"CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        #"DOWNLOAD_DELAY": 4
        }
    
    def start_requests(self):
        for index in range(len(self.postal_codes)):
            while self.page_num<=40:
                try:
                    code = self.postal_codes[index].lower()
                    link = f"https://www.rightmove.co.uk/house-prices/{code}.html?page={self.page_num}"
                    user_agent = random.choice(self.user_agent_list)
                    yield scrapy.Request(url=link, headers={'User-Agent': user_agent}, meta={'user_agent': user_agent}, callback=self.parse)
                except:
                    pass
                else:
                    self.page_num+=1
            self.page_num=1 

    def parse(self, response):
        user_agent=response.meta.get('user_agent')
        print("\n\n",user_agent)
        print("\n",response.url)
        
        script="".join([script for script in response.css("script::text").getall() if "window.__PRELOADED_STATE__ =" in script])
        script=json.loads(script.split("window.__PRELOADED_STATE__ =")[-1])

        properties=script["results"]["properties"]
        for property in properties:
            features={
                    "address":property["address"],
                    "propertyType": property["propertyType"],
                    "imageUrl": property["images"]["imageUrl"],
                    "price": property["transactions"][0]["displayPrice"],
                    "dateSold": property["transactions"][0]["dateSold"],
                    "tenure": property["transactions"][0]["tenure"],
                    "location": property["location"],
                }
            if "media" not in features["imageUrl"]:
                features["imageUrl"]="No Image"

            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
            yield response.follow(url=property["detailUrl"],headers={'User-Agent': user_agent},meta={'features': features}, callback=self.get_key_features)      

    def get_key_features(self,response):
        features=response.meta.get('features')
        features["keyFeatures"] = ", ".join(response.css("li[class='X4a4GM9iHdubzi2bdwYxA'] ::text").getall())
        
        yield features

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(RightMoveScraper)
    process.start()















