import scrapy
import scrapy.http
from scrapySpar.items import CategoryItem

from scrapySpar.utils import parser_utilities

import json
import re


class ProductSpider(scrapy.Spider):
    # Spider to crawl information about all products from a URL store. It needs a start url, a store_id is recomended
    # to be passed, to save the data correctly.

    name = "productSpider"

    custom_settings = {
        'FEED_EXPORT_ENCODING': 'utf-8',
		'FEEDS': { 'output/products_%(time)s.csv': { 'format': 'csv',}}
	}

    def __init__(self, start_urls, stores_ids=None, max_categories=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = start_urls.split(",")
        self.start_ids = stores_ids.split(",") if stores_ids else [None]*len(self.start_urls)
        self.max_categories = int(max_categories) if max_categories else None


    def start_requests(self):
        for url, store_id in zip(self.start_urls, self.start_ids):
            yield scrapy.Request(
                url,
                callback=self.parse,
                meta={'current_store_id': store_id}
            )
    
    def post_request(self, url, current_store_id, category: CategoryItem, page):
        if '/ajax/productsPagination' not in url:
            url = url + '/ajax/productsPagination'

        data = {
            'page_num': str(page),
            'page_container': '1',
            'category_id': category['category_id'],
            'featured_category_id': '0',
            'productsPerPage': '40',
            'params': '',
            'special_id': '',
        }


        # Obtener los headers actuales de Scrapy
        custom_headers = self.settings.get("DEFAULT_REQUEST_HEADERS", {}).copy()
        
        # Agregar o modificar el Content-Type
        custom_headers["content-type"] = "application/x-www-form-urlencoded; charset=UTF-8"

        return scrapy.FormRequest(
            url,
            formdata=data,
            method='POST',
            headers=custom_headers,
            callback=self.parse_product,
            meta={"page": page, 'category': category, 'current_store_id': current_store_id},
        )



    def parse(self, response: scrapy.http.Response):
        # Extract store information
        self.logger.info("Requesting store page...")
        html_content = response.text

        # Parser utilities
        categories = parser_utilities.get_main_categories_from_main_page(html_content)

        # Check if the user sent a store_id. If not check the store_id from the html content
        current_store_id = response.meta.get('current_store_id') if response.meta.get('current_store_id') else parser_utilities.get_current_store_id(html_content)

        if self.max_categories:
            categories = categories[:self.max_categories]
            self.logger.info(f"Limiting categories to {self.max_categories}.")

        for category in categories:

            category_item = CategoryItem(
                main_category=category['general_category'],
                sub_category=category['main_category'],
                sub_sub_category=category['name'],
                category_url=category['url'],
                category_id=category['id']
            )

            # Iterate through all the subcategories
            yield self.post_request(response.url, current_store_id, category_item, 1)

    
    def parse_product(self, response: scrapy.http.Response):
        self.logger.info("Requesting product page...")
        content = response.text

        json_content = json.loads(content)
        if json_content['success']:
            html_content = json_content['html']
            clean_html_content = re.sub(r'[\t\n\r]', '', html_content)

            if 'non sono presenti prodotti' in clean_html_content.lower():
                return  # End of the pagination
            
            products = parser_utilities.get_products_from_html(clean_html_content, response.meta['current_store_id'], response.meta['category'])
            for product in products:
                yield scrapy.Request(
                    product['product_url'],
                    callback=self.parse_product_details,
                    meta={'product': product}
                )

            # Keep the pagination active
            yield self.post_request(response.url, response.meta['current_store_id'], response.meta['category'], response.meta['page'] + 1)
            

    def parse_product_details(self, response: scrapy.http.Response):
        self.logger.info("Requesting product details page...")
        content = response.text

        product = response.meta['product']
        images_urls = parser_utilities.parse_details_product(content)['images_urls']

        product['image_urls'] = list(product['image_urls']) + images_urls

        # TODO: Add the rest of the products details like ingredients and nutritional values

        yield product
        


