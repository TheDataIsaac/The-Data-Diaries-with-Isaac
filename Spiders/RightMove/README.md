# RightMove Scraper

RightMove Scraper is a Python project that scrapes data from the UK property portal [RightMove](https://www.rightmove.co.uk/). It uses the scrapy framework to crawl and scrape the web pages, and saves the data as a JSON file.

## Features

RightMove Scraper can extract the following information about the properties listed on RightMove:

- address
- property type
- image URL
- price
- date sold
- tenure
- location
- key features

RightMove Scraper can scrape data for different postal codes in the UK, and can handle multiple pages of results.

## Usage

You can customize some settings for the scraper by editing the `rightmove.py` file. You can change the following variables:

- `postal_codes`: a list of postal codes in the UK that you want to scrape data for. You can add or remove postal codes as needed.
- `user_agent_list`: a list of user agents that are used for making requests to the website. You can add or remove user agents as needed.
- `custom_settings`: a dictionary of settings that are passed to the scrapy framework. You can change the output format, the concurrent requests, the download delay, and other settings as needed.


