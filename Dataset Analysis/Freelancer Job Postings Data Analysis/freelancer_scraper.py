import scrapy
import random
from scrapy.crawler import CrawlerProcess
import time
import random


class FreelancerSpider(scrapy.Spider):
    name = 'freelancerscraper'
    custom_settings = {
        "FEEDS": {
            "freelancerresult.json": {"format": "json"}
        },
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "DOWNLOAD_DELAY": 1,
    }

    current_page = 1

    def start_requests(self):
        for _ in range(1,201):
            url = f"https://www.freelancer.com/job-search/data-analysis/{self.current_page}/?languages=en&skills=1420,1039,1473,13,55,601,1077,36,334,889,2562,1503,68,696,305,1253,2528,1681,1040,2126"
            headers = self.get_headers()
            try:
                yield scrapy.Request(url=url, headers=headers, callback=self.parse)
            except:
                pass
            self.current_page += 1
            time.sleep(int(random.choice(range(0,3))))

    def parse(self, response):
        with open("ress.html", "w", encoding = "utf-8") as file:
            file.write(response.text)

        links = response.css("div[class='JobSearchCard-primary-heading'] a::attr(href)").getall()
        headers = self.get_headers()
        for link in links:
            if not "/login?goto" in link:
                link = "https://www.freelancer.com/" + link
                try:
                    yield response.follow(url=link, headers=headers, callback=self.get_data)
                except:
                    pass

    def get_data(self, response):
        with open("pagg.html", "w", encoding = "utf-8") as file:
            file.write(response.text)
        try:
            job_title = response.css("h1[class='PageProjectViewLogout-projectInfo-title'] ::text").get()
            unfiltered_tags =  response.css("p[class='PageProjectViewLogout-detail-tags'] *::text").getall()
            tags = list(filter(None, map(str.strip, unfiltered_tags)))
            projectId = response.css("p[class='PageProjectViewLogout-detail-projectId']::text").get()
            description_list = response.css("div[class='PageProjectViewLogout-detail'] p *::text").getall()
            job_description = []
            for description in description_list:
                if description not in [projectId] + unfiltered_tags:
                    job_description.append(description.strip())
                
            job_description = " ".join(job_description).replace("\n","")
            projectId= projectId.split()[-1]
            price = response.css("p[class='PageProjectViewLogout-projectInfo-byLine'] ::text").get().replace(" / ","/")[1:].split()
            price_range=price[0]
            rate = price[1]
            client_location = response.css("span[itemprop='addressLocality'] ::text").get().strip()
            client_average_rating = response.css("span[class='PageProjectViewLogout-detail-clientStats-rating-average'] ::text").get().strip()
            client_review_count = response.css("span[class='PageProjectViewLogout-detail-clientStats-rating-review-count'] ::text").get().strip()
        except:
            pass
        else:
            data = {
                "job_title" :job_title,
                "projectId" : projectId,
                "job_description" : job_description,
                "tags" : tags,
                "price_range" : price_range,
                "rate" : rate,
                "client_location" : client_location,
                "client_average_rating" : client_average_rating,
                "client_review_count" : client_review_count,
            }
            yield data

    def get_headers(self):
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 OPR/95.0.0.",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.47",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 OPR/102.0.0.",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.0 Safari/537.36"
        ]
        headers={
            "User-Agent": random.choice(user_agents),
        }

        return headers    

if __name__ == "__main__":
    # Configure settings for the CrawlerProcess
    process = CrawlerProcess()
    process.crawl(FreelancerSpider)
    process.start()

    # FreelancerSpider.parse(FreelancerSpider, "")

url2 = "https://www.freelancer.com/projects/excel/data-analytics-high-level-excel"
url3 = "https://www.freelancer.com/projects/machine-learning/performance-analysis-machine-learning-37411930"