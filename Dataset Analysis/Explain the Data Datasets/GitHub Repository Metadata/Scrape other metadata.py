import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.exceptions import DropItem # To handle potential item validation later if needed
import json
import os
import random
import re
# Optional: Define a Scrapy Item for structure (good practice)
# class GhRepoItem(scrapy.Item):
#     url = scrapy.Field()
#     file_list = scrapy.Field()
#     file_count = scrapy.Field()
#     readme_preview = scrapy.Field()
#     sidebar_about_text = scrapy.Field()
#     commit_count_display = scrapy.Field()

# --- Custom Pipeline for JSON Lines Output ---
class JsonLinesPipeline:
    def __init__(self):
        self.file = None
        self.output_filename = 'scraped_data.jsonl' # Using .jsonl extension

    def open_spider(self, spider):
        # Open the file in append mode, creating it if it doesn't exist
        self.file = open(self.output_filename, 'a', encoding='utf-8')
        spider.logger.info(f"Opened output file {self.output_filename} in append mode.")

    def close_spider(self, spider):
        if self.file:
            self.file.close()
            spider.logger.info(f"Closed output file {self.output_filename}.")

    def process_item(self, item, spider):
        # Convert item (dictionary or Item object) to a JSON string
        # Use ensure_ascii=False for broader character support
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        try:
            self.file.write(line)
            # Flush buffer to ensure it's written immediately (important for resilience)
            self.file.flush()
        except Exception as e:
            spider.logger.error(f"Error writing item to {self.output_filename}: {e}")
            # Optional: Re-raise or handle differently if needed
            # raise DropItem(f"Failed to write item to file: {item.get('url')}") from e
        return item # Must return the item for other pipelines (if any)
# --- End Pipeline ---


class GHHTMLSpider(scrapy.Spider):
    name = 'gh_html_spider'
    # No static start_urls

    def __init__(self, *args, **kwargs):
        super(GHHTMLSpider, self).__init__(*args, **kwargs)
        self.visited_links_file = 'visited_links.json'
        self.html_output_file = 'repo_html.html' # Optional
        self.links_file = 'extracted_github_links.json'

        # --- Load start_urls from JSON file ---
        self.start_urls = []
        if os.path.exists(self.links_file):
            try:
                with open(self.links_file, 'r') as f:
                    self.start_urls = json.load(f)
                    if not isinstance(self.start_urls, list):
                        self.logger.error(f"{self.links_file} does not contain a JSON list.")
                        self.start_urls = []
                    else:
                         self.logger.info(f"Loaded {len(self.start_urls)} URLs from {self.links_file}")
            except json.JSONDecodeError:
                self.logger.error(f"Error decoding JSON from {self.links_file}.")
            except Exception as e:
                 self.logger.error(f"Error reading {self.links_file}: {e}")
        else:
            self.logger.error(f"{self.links_file} not found.")

        # --- Load visited_links.json ---
        if os.path.exists(self.visited_links_file):
            try:
                with open(self.visited_links_file, 'r') as f:
                    self.visited_links = set(json.load(f))
                    self.logger.info(f"Loaded {len(self.visited_links)} visited URLs from {self.visited_links_file}")
            except json.JSONDecodeError:
                self.logger.warning(f"Could not decode {self.visited_links_file}. Starting with empty set.")
                self.visited_links = set()
            except Exception as e:
                 self.logger.error(f"Error reading {self.visited_links_file}: {e}")
                 self.visited_links = set()
        else:
            self.visited_links = set()
            self.logger.info(f"{self.visited_links_file} not found. Starting with empty set.")

    def get_headers(self):
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1 Safari/605.1.15",
            "Mozilla/5.0 (Linux; Android 9; Pixel 3 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Mobile Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:25.0) Gecko/20100101 Firefox/25.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
        ]
        return {
            "User-Agent": random.choice(user_agents)
        }

    def start_requests(self):
        if not self.start_urls:
             self.logger.error("No URLs to crawl. Check extracted_github_links.json.")
             return

        urls_to_crawl_count = 0
        for url in self.start_urls:
            if url not in self.visited_links:
                 self.logger.info(f"Queueing request for new URL: {url}")
                 yield scrapy.Request(url=url, headers=self.get_headers(), callback=self.parse)
                 urls_to_crawl_count += 1
            else:
                 self.logger.info(f"URL already visited, skipping: {url}")

        self.logger.info(f"Finished queueing. Total new URLs to crawl in this run: {urls_to_crawl_count}")

    def parse(self, response):
        self.logger.info(f"Parsing: {response.url}")

        # --- Extraction Logic (Remains the same) ---
        file_list = []
        file_rows = response.css('tbody tr.react-directory-row')
        for row in file_rows:
            is_directory = row.css('svg.icon-directory').get() is not None
            file_type = 'folder' if is_directory else 'file'
            name = row.xpath('.//div[contains(@class, "react-directory-filename-cell")]//a/text()').get()
            if name:
                file_list.append({'name': name.strip(), 'type': file_type})

        readme_preview_raw = response.css('article.markdown-body p ::text').getall()
        readme_preview = ' '.join(readme_preview_raw).strip() if readme_preview_raw else "Readme preview not found"

        sidebar_about_text_raw = response.xpath('//h2[contains(text(),"About")]/following-sibling::p/text()').getall()
        sidebar_about_text = ' '.join(sidebar_about_text_raw).strip() if sidebar_about_text_raw else "About text not found"

        commit_text = response.xpath('//a[contains(@href, "/commits/")]//span[contains(text(), "Commit")]/text()').get()
        commit_count_display = "Commit count not found"
        if commit_text:
             match = re.search(r'(\d+)\s+Commit', commit_text)
             if match:
                 commit_count_display = f"{match.group(1)} commits"

        # --- Yield the scraped data (as dictionary or GhRepoItem) ---
        scraped_data = {
            'url': response.url,
            'file_list': file_list,
            'file_count': len(file_list),
            'readme_preview': readme_preview,
            'sidebar_about_text': sidebar_about_text,
            'commit_count_display': commit_count_display,
        }
        # Optional: yield GhRepoItem(scraped_data) if using Items
        yield scraped_data


        # --- Track visited links after successful parse ---
        current_url = response.url
        if current_url not in self.visited_links:
            self.visited_links.add(current_url)
            try:
                # Save visited links immediately after adding one
                with open(self.visited_links_file, 'w') as f:
                    json.dump(list(self.visited_links), f, indent=2)
                self.logger.info(f"Successfully processed and recorded {current_url} in {self.visited_links_file}")
            except Exception as e:
                 self.logger.error(f"Error writing to {self.visited_links_file}: {e}")
        else:
             self.logger.info(f"URL {current_url} was already in visited set upon parse completion.")


# --- Run with CrawlerProcess, using ITEM_PIPELINES ---
if __name__ == "__main__":
    if not os.path.exists('extracted_github_links.json'):
         print("Error: extracted_github_links.json not found. Please create it with a list of URLs.")
    else:
        process = CrawlerProcess(settings={
            'LOG_LEVEL': 'INFO',
            # --- Activate the custom pipeline ---
            'ITEM_PIPELINES': {
                # The key is the path to your pipeline class, value is its order (lower runs first)
                 __name__ + '.JsonLinesPipeline': 1, # Using __name__ to dynamically get current module
                 # Add other pipelines here if needed, e.g., '.MyValidationPipeline': 2
            },
            # --- FEEDS setting is no longer needed for this output file ---
            # 'FEEDS': { ... },
            'DOWNLOAD_DELAY': 1,
            'AUTOTHROTTLE_ENABLED': True,
        })
        process.crawl(GHHTMLSpider)
        process.start()