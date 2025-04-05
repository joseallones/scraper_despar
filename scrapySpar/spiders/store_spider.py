import scrapy
import scrapy.http

from scrapySpar.utils import parser_utilities


class StoreSpider(scrapy.Spider):
    # Spider to crawl Despar stores and obtain its information


    name = "storeSpider"
    start_urls = ['https://shop.despar.com/']

    custom_settings = {
		'FEEDS': { 'output/stores_%(time)s.csv': { 'format': 'csv',}}
	}


    def parse(self, response: scrapy.http.Response):
        # Extract store information
        self.logger.info("Requesting main page...")
        html_content = response.text

        # Parser utiltities
        home_delivery = parser_utilities.get_home_delivery_stores(html_content)
        pick_up = parser_utilities.get_pick_up_stores(html_content)

        all_stores = home_delivery + pick_up

        for store in all_stores:
            if store.get('fullfillment_method') == 'Home Delivery' and store.get('url'):
                self.logger.info(f"Requesting store page: {store.get('url')}")
                yield scrapy.Request(
                    url=store.get('url'),
                    callback=self.parse_particular_store,
                    meta={'store': store, 'stores': pick_up},
                )
            else:
                yield store

    
    def parse_particular_store(self, response: scrapy.http.Response):
        # Extract store information from a particular store, accessing its main webpage
        store = response.meta['store']
        all_stores = response.meta['stores']
        stores_id = {store.get('store_id'): store.get('address') for store in all_stores}
        stores_types = {store.get('store_id'): store.get('store_type') for store in all_stores}

        html_content = response.text
        
        store_id = parser_utilities.get_current_store_id(html_content)
        if int(store_id) in stores_id:
            address = stores_id[int(store_id)]
            store_type = stores_types[int(store_id)]
            store['address'] = address
            store['store_type'] = store_type
            

        store['store_id'] = int(store_id)

        yield store
