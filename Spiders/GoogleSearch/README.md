
# GoogleScraper
A scrapy spider that scrapes Google search results for a given query.

## Requirements 
- scraper_params.py file that contains the user agents, initial parameters, pagination parameters, and headers for the spider

## Usage
- Edit the query, user_agents, pagination_params, initial_params, custom_headers, and pages variables in the GoogleScraper class according to your needs.
- Run the spider with `scrapy runspider google_scraper.py`
- The scraped data will be saved in a JSON file named searchresult.json in the same directory as the spider.

## How it works
- The spider generates a list of URLs for each page of the Google search results using the base URL and the custom parameters.
- The spider randomly selects a user agent from the user_agents list and sends a GET request to each URL with the custom headers.
- The spider parses the response and extracts the title and link of each result using CSS selectors.
- The spider yields each result as a dictionary and appends it to the scraped_data list to avoid duplicates.
- The spider stops when it reaches the specified number of pages or when there are no more results.
