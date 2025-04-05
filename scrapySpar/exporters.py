from scrapy.exporters import CsvItemExporter
from scrapy.item import Item

class FlattenCsvItemExporter(CsvItemExporter):
    # Method to flatten an item and process it into a CSV format

    def flatten_item(self, item):
        flattened = {}

        if isinstance(item, Item):
            item = dict(item)  

        for key, value in item.items():
            new_key = f"{key}"

            if isinstance(value, Item) or isinstance(value, dict):  
                nested = self.flatten_item(dict(value))
                flattened.update(nested)
            elif not value:
                flattened[new_key] = "N/A"
            else:
                flattened[new_key] = value  

        return flattened


    def export_item(self, item):
        item = self.flatten_item(item)
        return super().export_item(item) 
