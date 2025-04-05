# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
import re
from datetime import datetime


class ProductItem(scrapy.Item):
    # Instance of product item

    unique_id = scrapy.Field() # Dinamic

    product_id = scrapy.Field()
    store_id = scrapy.Field()

    date_extraction = scrapy.Field() # Dinamic
    hour_extraction = scrapy.Field() # Dinamic

    name = scrapy.Field()
    brand = scrapy.Field()

    promotion = scrapy.Field()
    percent_promotion = scrapy.Field() # Dinamic
    deadline_promotion = scrapy.Field() # Dinamic

    price = scrapy.Field()
    old_price = scrapy.Field()

    image_urls = scrapy.Field()
    main_image_url = scrapy.Field() # Dinamic

    weight_volume = scrapy.Field()
    value_wv = scrapy.Field() # Dinamic
    unit_wv = scrapy.Field() # Dinamic

    price_per_wv = scrapy.Field()
    value_price_per_wv = scrapy.Field() # Dinamic
    unit_price_per_wv = scrapy.Field() # Dinamic

    product_url = scrapy.Field()
    labels = scrapy.Field()
    category = scrapy.Field()

    
class CategoryItem(scrapy.Item):
    # Instance of category item
    main_category = scrapy.Field()
    sub_category = scrapy.Field()
    sub_sub_category = scrapy.Field()
    category_url = scrapy.Field()
    category_id = scrapy.Field()


class StoreItem(scrapy.Item):
    # Instance of store item
    zip_code = scrapy.Field()
    store_id = scrapy.Field()
    fullfillment_method = scrapy.Field()
    address = scrapy.Field()
    url = scrapy.Field()
    ref_physical_store = scrapy.Field()
    store_type = scrapy.Field()


class AddressItem(scrapy.Item):
    # Instance of address item
    address = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()