# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapySpar.items import ProductItem, StoreItem

from datetime import datetime
import re


# Two pipelines, one for the product items and one for the stores items.
    

class ProductPipeline:

    def process_item(self, item, spider):
        
        if isinstance(item, ProductItem):
            current_year = datetime.now().year

            # Brand
            if not item['brand']:
                item['brand'] = 'Altro'

            # Add unique id
            item['unique_id'] = f"{item['store_id']}_{item['product_id']}"

            # Add date
            item['date_extraction'] = datetime.now().strftime('%d/%m/%Y')
            item['hour_extraction'] = datetime.now().strftime('%H:%M')

            # Promotion related
            promotion = item['promotion']
            if promotion:
                match = re.search(r'(\d+)%', promotion, re.IGNORECASE) if promotion else None
                item['percent_promotion'] = match.group(1) if match else None
                match = re.search(r'fino al (\d+/\d+)', promotion, re.IGNORECASE) if promotion else None
                item['deadline_promotion'] = f'{match.group(1)}/{current_year}' if match else None

            # Weigh-Volume related
            weight_volume = item['weight_volume']
            if weight_volume:
                match = re.search(r'([\d,]+) (\w+)?', weight_volume, re.IGNORECASE) if weight_volume else None
                item['value_wv'] = float(match.group(1).replace(",", ".")) if match else None
                if match and match.group(2):
                    item['unit_wv'] = match.group(2).lower()
                else:
                    item['unit_wv'] = None

            # Price per weight-volume related
            price_per_wv = item['price_per_wv']
            if price_per_wv:
                match = re.search(r'([\d,]+) € al (\w+)?', price_per_wv, re.IGNORECASE) if price_per_wv else None
                item['value_price_per_wv'] = float(match.group(1).replace(",", ".")) if match else None
                if match and match.group(2):
                    item['unit_price_per_wv'] = match.group(2).lower()
                else:
                    item['unit_price_per_wv'] = None

            # Image related
            image_urls = item['image_urls']
            if image_urls:
                item['main_image_url'] = image_urls[0]


            # Reorder item
            ordered_item = {
                'unique_id': item.get('unique_id'),  # Dynamic
                'product_id': item.get('product_id'),
                'store_id': item.get('store_id'),
                'date_extraction': item.get('date_extraction'),  # Dynamic
                'hour_extraction': item.get('hour_extraction'),  # Dynamic
                'name': item.get('name'),
                'brand': item.get('brand'),
                'promotion': item.get('promotion'),
                'percent_promotion': item.get('percent_promotion'),  # Dynamic
                'deadline_promotion': item.get('deadline_promotion'),  # Dynamic
                'price': item.get('price'),
                'old_price': item.get('old_price'),
                'weight_volume': item.get('weight_volume'),
                'value_wv': item.get('value_wv'),  # Dynamic
                'unit_wv': item.get('unit_wv'),  # Dynamic
                'price_per_wv': item.get('price_per_wv'),
                'value_price_per_wv': item.get('value_price_per_wv'),  # Dynamic
                'unit_price_per_wv': item.get('unit_price_per_wv'),  # Dynamic
                'labels': item.get('labels'),
                'category': item.get('category'),
                'product_url': item.get('product_url'),
                'main_image_url': item.get('main_image_url'),  # Dynamic
                'image_urls': item.get('image_urls'),
            }

            item.clear()
            item.update(ordered_item)


        return item
    

class StorePipeline:

    def process_item(self, item, spider):

        if isinstance(item, StoreItem):

            # Reorder item
            ordered_item = {
                'store_id': item.get('zip_code') if 'zip_code' in item else item.get('store_id'),
                'ref_physical_store': item.get('store_id') if 'zip_code' in item else None,
                'fullfillment_method': item.get('fullfillment_method'),
                'store_type': item.get('store_type'),
                'address': item.get('address'),
                'url': item.get('url'),
            }

            item.clear()
            item.update(ordered_item)
        
        return item