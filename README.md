# Despar Scraper

This repository contains a web scraping project built with Scrapy for extracting data from the Despar website, including store details and product catalogs.
## Project Structure

```
├── README.md
├── dags
│   └── despar-dag.py               # Airflow DAG definition for orchestrating the scraper
├── despar_scraper.py               # "Main" script that can be used as a quick way to launch both spiders (more details below)
├── requirements.txt                # Python dependencies
├── scrapy.cfg                      # Scrapy configuration
└── scrapySpar                      # This folder contains all the core logic for the Scrapy spiders.
    ├── __init__.py
    ├── exporters.py                # Custom exporters (if needed)
    ├── items.py                    # Scrapy item definitions
    ├── middlewares.py              # Custom middlewares (proxy configuration is set here)
    ├── pipelines.py                # Item processing pipelines
    ├── settings.py                 # Scrapy project settings
    ├── spiders
    │   ├── __init__.py
    │   ├── product_spider.py       # Spider to extract product data
    │   └── store_spider.py         # Spider to extract store data
    └── utils
        └── parser_utilities.py     # Utility functions for parsing
```




## Requirements

Install dependencies using:

```bash
pip install -r requirements.txt
```

---

## Running the Scraper

To run the scraper, you can use the `despar_scraper.py` script, which acts as the main entry point. 
This script will launch both spiders to extract data from the stores and the products of two default stores (this can be configured): 

https://shop.despar.com/spesa-consegna-domicilio/65128
https://shop.despar.com/spesa-ritiro-negozio/rende-interspar-via-silvio-pellico-18

Note that the following instructions are for running the scraper directly from the terminal, without the need to deploy it in Airflow.
```bash

python despar_scraper.py
```

Alternatively, the spiders can be run separately as follows:

Store spider:

```bash
scrapy crawl storeSpider
```
Product spider:

```bash
scrapy crawl productSpider -a start_urls=shop_urls
```
where shop_urls is a comma-separated list of shop URLs that you want to scrape.

Example:
```bash
scrapy crawl productSpider -a start_urls='https://shop.despar.com/spesa-ritiro-negozio/rende-interspar-via-silvio-pellico-18'
```



## Output

All scraped data is saved in the `output/` folder in CSV format, including:
- **products_*.csv**: detailed product information.
- **stores_*.csv**: metadata about available Despar stores.