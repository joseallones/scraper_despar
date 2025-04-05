from traceback import print_tb

from bs4 import BeautifulSoup
import re
import json


from scrapySpar.items import StoreItem, AddressItem, ProductItem


def get_home_delivery_stores(html_main_page, at_home_url='https://shop.despar.com/spesa-consegna-domicilio/'):
    # Function to return all zip codes found for "Home Delivery" shops
    stores = list()

    soup = BeautifulSoup(html_main_page, 'html.parser')

    form = soup.find('form', id="deliveryZipCodeForm")
    if form:
        script = form.find('script').text

        cities = None
        match = re.search(r'(CitiesJson.*?)=(.*?);', script, re.DOTALL | re.MULTILINE)
        if match:
            cities = json.loads(match.group(2).strip())
            cities = {str(element['Id']): element['Name'] for sublist in cities.values() for element in sublist}


        match = re.search(r'(ZipCode.*?)=(.*?);', script, re.DOTALL | re.MULTILINE)
        if match:
            zip_codes = json.loads(match .group(2).strip())

            for key, sublist in zip_codes.items():
                for element in sublist:
                    store = StoreItem(
                        zip_code=element['Id'],
                        fullfillment_method='Home Delivery',
                        url=at_home_url + element['Id'],
                        address=AddressItem(address=cities[key], latitude=0, longitude=0)
                    )

                    stores.append(store)

            return stores


def get_pick_up_stores(html_main_page):
    # Function to return all zip codes found for "Pick Up" shops
    stores = list()

    soup = BeautifulSoup(html_main_page, 'html.parser')

    form = soup.find('form', id="deliveryStoreForm")
    if form:
        script = form.find('script').text

        match = re.search(r'(stores4MapsJson.*?)=(.*?);', script, re.DOTALL | re.MULTILINE)
        if match:
            stores_json = json.loads(match.group(2).strip())

            for element in stores_json:
                store = StoreItem(
                    store_id=element['StoreId'],
                    fullfillment_method='Pick Up in Store',
                    url=element['Url'],
                    address=AddressItem(
                        address=element['Address'],
                        latitude=element['Lat'],
                        longitude=element['Long']
                    ),
                    store_type=element['Type']
                )

                stores.append(store)

            return stores
        

def get_current_store_id(html_content):
    # Function to return the current store id
    soup = BeautifulSoup(html_content, 'html.parser')

    script_current_store = soup.find('script', string=lambda t: t and 'currentStoreId' in t)
    if script_current_store:
        text_script = script_current_store.text
        matches = re.finditer(r'(.*?)=(.*?);', text_script, re.DOTALL | re.MULTILINE)
        for match in matches:
            if 'currentStoreId' in match.group(1):
                current_store_id = match.group(2).strip().replace('"', '')
                return current_store_id


def get_main_categories_from_main_page(html_main_page, url='https://shop.despar.com'):
    # Function to get all the main categories from a shop
    categories = list()

    soup = BeautifulSoup(html_main_page, 'html.parser')
    categories_div = soup.find('div', class_='main-navigation__wrap')

    for category_section in categories_div.find_all('div', class_='main-navigation__item--container'):

        general_category = category_section.find('div', class_='main-navigation__item--title').text.strip()
        general_link = url + category_section.find('a').attrs.get('href')
        categories_elements = category_section.find_all('div', class_='columns__item')


        main_categories = list()
        for category in categories_elements:
            main_category = category.find('div', class_='columns__item--mobile')
            name = main_category.text.strip()
            link = url + main_category.find('a').attrs.get('href')

            subcategories = list()
            subcategories_element = category.find('div', class_='columns__item--sub')
            for element in subcategories_element.find_all('div'):
                sub_name = element.text.strip()
                sub_link = url + element.find('a').attrs.get('href')
                subcategories.append({'name': sub_name, 'url': sub_link, 'id': sub_link.split('_')[-1]})

            main_categories.append({'name': name, 'url': link, 'id': link.split('_')[-1], 'subcategories': subcategories})

        categories.append({'general_category': general_category, 'url': general_link, 'main_categories': main_categories, 'id': general_link.split('_')[-1]})

    categories = [{'name': subcategory['name'], 'general_category': category['general_category'],
                    'main_category': main_category['name'], 'url': subcategory['url'], 'id': subcategory['id']} for category in
                    categories for main_category in category['main_categories'] for subcategory in
                    main_category['subcategories']
                ]

    return categories


def get_products_from_html(html_product, store_id, category=None, url='https://shop.despar.com'):
    # Function to return all products found in the html. Works for the main page but also for the single page html
    products = list()

    soup = BeautifulSoup(html_product, 'html.parser')

    # Find section products
    sections = soup.find_all('section')

    for section in sections:
        data_order = section.find('div', attrs={'data-order': True})
        order_attrs = data_order.attrs

        order_attrs = {key.replace('data-', ''): value for key, value in order_attrs.items() if key != 'data-order'}

        # Attribute of products
        product_id = order_attrs.get('id') # Product ID
        product_name = order_attrs.get('name') # Product Name

        # Brand
        if order_attrs['brand']:
            product_brand = order_attrs.get('brand')
        else:
            product_brand = None

        product_img_urls = [order_attrs.get('img-src')] # First image
        price = float(order_attrs.get('price').replace('€', '').replace(',', '.')) # Price

        # Old price
        if order_attrs['old-price']:
            old_price = float(order_attrs.get('old-price').replace('€', '').replace(',', '.'))
        else:
            old_price = None

        # Labels
        labels = list()
        span_labels = section.find_all('span', class_='icon', attrs={'data-tooltip': True})
        for span in span_labels:
            labels.append(span.attrs.get('data-tooltip'))

        # Promotion
        if section.find('span', class_='discount'):
            discount = section.find('span', class_='discount').text
        else:
            discount = None

        if section.find('span', class_='upto'):
            up_to = section.find('span', class_='upto').text
        else:
            up_to = None

        if discount or up_to:
            promotion = discount + ' - ' + up_to
        else:
            promotion = None

        # Weight-volume
        meta = order_attrs.get('meta')
        weight_volume = meta.split(' - ')[0]

        # Price per weight-volume
        price_per_w_v = meta.split(' - ')[-1]

        # Product URL
        product_url = url + section.find('div', class_='product-img').find('a').attrs.get('href')

        # Append product
        products.append(
            ProductItem(
                product_id=product_id,
                store_id=store_id,
                name=product_name,
                brand=product_brand,
                promotion=promotion,
                price=price,
                old_price=old_price,
                image_urls=product_img_urls,
                weight_volume=weight_volume,
                price_per_wv=price_per_w_v,
                product_url=product_url,
                labels=labels,
                category=category
            )
        )

    return products


def parse_details_product(html_content):
    # Function to parse the HTML content of a product details page
    images_urls = list()

    soup = BeautifulSoup(html_content, 'html.parser')

    detailed_images = soup.find('div', id='ulImage')
    if detailed_images:
        for img in detailed_images.find_all('img'):
            images_urls.append(img.attrs.get('data-original'))

    return {
        'images_urls': images_urls,
    }
