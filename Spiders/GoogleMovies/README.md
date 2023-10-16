# GoogleMovies: A Scrapy Project to Scrape Movie Information from Wikipedia

This is a scrapy project that scrapes movie information from [Wikipedia](https://en.wikipedia.org/wiki/List_of_Walt_Disney_Pictures_films), the free online encyclopedia. It focuses on the movies produced by Walt Disney Pictures, one of the leading film studios in the world. It is part of my scrapy series, where I show how to use scrapy to crawl and scrape various websites.

## Project Overview

The project consists of one spider, `googlescraper`, that follows the rules and logic defined in `googlescraper.py`. The spider starts from the list page of Walt Disney Pictures films, and follows the links to each movie page to extract the information from the infobox table. The scraped data is saved to a JSON file named `movies.json` in the same directory as the script.

The data includes the following fields:

- title: The title of the movie
- Directed by: The name(s) of the director(s)
- Produced by: The name(s) of the producer(s)
- Screenplay by: The name(s) of the screenwriter(s)
- Story by: The name(s) of the story writer(s)
- Based on: The source material of the movie
- Starring: The name(s) of the main actor(s)
- Music by: The name(s) of the composer(s)
- Cinematography: The name(s) of the cinematographer(s)
- Edited by: The name(s) of the editor(s)
- Production company: The name(s) of the production company(ies)
- Distributed by: The name(s) of the distributor(s)
- Release date: The date(s) of release
- Running time: The duration of the movie
- Country: The country(ies) of origin
- Language: The language(s) of the movie
- Budget: The budget of the movie
- Box office: The box office revenue of the movie

## How to Run

To run this project, you need to have scrapy installed on your system. You can install scrapy using `pip`:

`pip install scrapy`

Then, you can clone this repository or download the files to your local machine. Navigate to the directory where the files are located, and run the following command:

`scrapy crawl googlescraper`

Alternatively, you can use the command line option `-o movies.json` to save the data to the JSON file directly:

`scrapy runspider googlescraper.py -o movies.json`

## Note

Please respect Wikipedia's terms of use and robots.txt when using this project. Do not scrape excessively or maliciously, and do not use the scraped data for any commercial or illegal purposes.
