
import subprocess



def storeSpider():
    subprocess.run(["scrapy", "crawl", "storeSpider"], check=True)


def productSpider(home_delivery_id, home_delivery_url, pick_up_id, pick_up_store_url):
    subprocess.run(["scrapy", "crawl", "productSpider",
                     "-a", f'stores_ids={home_delivery_id},{pick_up_id}',
                     '-a',f'start_urls={home_delivery_url},{pick_up_store_url}'],
                    check=True)


if __name__ == '__main__':

    print("Starting Store Spider!")
    storeSpider()
    print("Stores parsed")

    # Hardcoded values:
    home_delivery_id = "65128"
    home_delivery_url = "https://shop.despar.com/spesa-consegna-domicilio/65128"
    pick_up_id = "33838"
    pick_up_store_url = "https://shop.despar.com/spesa-ritiro-negozio/rende-interspar-via-silvio-pellico-18"

    productSpider(home_delivery_id, home_delivery_url, pick_up_id, pick_up_store_url)
    print("Products parsed")


