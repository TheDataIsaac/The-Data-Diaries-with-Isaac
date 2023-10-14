# Scraping Images from Twitter using Nitter

In this project, we scrape images from Twitter using a website called Nitter.

## What is Nitter?

Nitter is an alternative front-end for Twitter that does not require JavaScript or a logged-in user. It allows you to browse Twitter anonymously and without any tracking or ads. It also provides RSS feeds for profiles, hashtags, and searches.

## Why use Nitter?

One of the challenges of scraping data from Twitter is that it requires a logged-in user and uses JavaScript to render the content dynamically. This makes it difficult to use Scrapy's default HTML parser and request methods. You would need to use tools like Splash or Selenium to render the JavaScript and simulate a browser session.

However, using Nitter, we can bypass these challenges and scrape the data easily using Scrapy's built-in features. Nitter provides a simple and clean HTML interface that can be parsed with Scrapy's CSS selectors or XPath expressions. It also does not require any authentication or cookies, so we can make requests without any headers or parameters.

## How to use this code?

This code is a standalone Scrapy spider that scrapes images from the Twitter account of **IsaacMustTalk** using Nitter. The code does the following things:

- It defines a list of user agents to randomly choose from when making requests to avoid being blocked by the website.
- It starts from the search URL that filters the tweets by the username, images, no retweets and no replies.
- It parses the response and extracts the image URLs from the HTML elements using CSS selectors.
- It saves the images to the local directory using the requests library and the image names.
- It runs the spider using the CrawlerProcess class.

To use this code, you need to have Scrapy and requests installed on your system. You can install them using pip:

`pip install scrapy`

`pip install requests`

You also need to save the code in a Python file, for example, `mediascraper.py`. Then, you can run the spider from your terminal:

`python mediascraper.py`

The code will scrape all the images from IsaacMustTalk's account and save them in your current directory. You can change the username to any other Twitter user by modifying this line in the code:

`username = "IsaacMustTalk"`

You can also change other parameters in the search URL, such as filtering by videos, links, hashtags, etc. For more information on how to use Nitter's search features, you can visit their website.
