import datetime
from ebaysdk.exception import ConnectionError
from ebaysdk.finding import Connection
from EbayItem import EbayItem
from ebay_category import ebay_category


class EbaySearcher:
    def __init__(self, dolar):
        self.dolar = dolar

    def getItem(self, keywords, min_price, max_price):
        print(keywords)
        if 'Linkin Park' in keywords:
            gift = self.getGift('Linkin Park', min_price, max_price)
            if gift:
                print("BUSQUEDA EBAY:",'Linkin Park')
                return gift
        for kw in keywords:
            print("QUERY:", kw)
            gift = self.getGift(kw, min_price, max_price)
            if gift:
                print("BUSQUEDA EBAY:",kw)
                return gift
        return

    def getGift(self, query, min_price, max_price):
        try:
            api = Connection(appid='JavierLo-Cualquie-PRD-d99e611cc-c460f656', config_file=None)
            response = api.execute('findItemsAdvanced', {'keywords': query})

            try:
                assert(response.reply.ack == 'Success')
            except AssertionError:
                print("ERROR: EMPTY QUERY")
                return

            assert(type(response.reply.timestamp) == datetime.datetime)
            try:
                assert(type(response.reply.searchResult.item) == list)
            except AttributeError:
                print("ERROR: NO RESULTS")
                return

            item = response.reply.searchResult.item[0]
            assert(type(item.listingInfo.endTime) == datetime.datetime)
            assert(type(response.dict()) == dict)

            response_items_list = response.dict()["searchResult"]["item"]
            items = []
            try:
                for i in range(len(response_items_list)):
                    item_title = response_items_list[i]["title"]
                    item_url = response_items_list[i]['viewItemURL']
                    item_photo = response_items_list[i]['galleryURL']
                    item_value_USD = float(response_items_list[i]["sellingStatus"]['convertedCurrentPrice']['value'])
                    item_value_CLP = int(item_value_USD * self.dolar)
                    item_currencyId = response_items_list[i]["sellingStatus"]['convertedCurrentPrice']['_currencyId']
                    if min_price <= item_value_CLP <= max_price:
                        new_item = EbayItem(item_title, item_url, item_photo, item_value_CLP)
                        items.append(new_item)
            except KeyError:
                print("ERROR: NO RESULTS")
                return

            if not items:
                print("ERROR: NO RESULTS")
                return

            #items.sort(key=lambda x: x.value, reverse=False)
            print(len(items))
            return list(set(items[0:(min(20,len(items)))]))

        except ConnectionError as e:
            print(e)
            print(e.response.dict())
            return