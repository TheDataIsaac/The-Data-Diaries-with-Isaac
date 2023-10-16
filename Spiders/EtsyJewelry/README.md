# Scrapy Series: Etsy Scraper

This is a scrapy project that scrapes handmade jewelry listings from [Etsy](https://www.etsy.com/), a global online marketplace for unique and creative goods. It is part of my Scrapy series, where I demonstrate how to use scrapy to crawl and scrape various websites.

## Project Overview

The project consists of one spider, `etsyscraper`, that follows the rules and logic defined in `etsyscraper.py`. The spider starts from the [search page](https://www.etsy.com/search?q=handmade+jewelry) for handmade jewelry, and follows the listing links and pagination links to extract the title, brand, and price of each item. The scraped data is saved to a JSON file named `jewelry.json` in the same directory as the script.

## How to Run

To run this project, you need to have [scrapy] installed on your system. You can install scrapy using `pip`:

`pip install scrapy`

Then, you can clone this repository or download the files to your local machine. Navigate to the directory where the files are located, and run the following command:

`scrapy crawl etsyscraper`

Alternatively, you can use the command line option `-o jewelry.json` to save the data to the JSON file directly:

`scrapy runspider etsyscraper.py -o jewelry.json`

## Note

Please respect Etsy's terms of use and robots.txt when using this project. Do not scrape excessively or maliciously, and do not use the scraped data for any commercial or illegal purposes.
