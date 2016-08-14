from EbaySearcher import EbaySearcher

DOLAR = 660
MIN_PRICE = 8000
MAX_PRICE = 10000
KEYWORD = {"Music Lovers": ['avicii']}

ebay = EbaySearcher(dolar=DOLAR)
gift = ebay.getItem(KEYWORD, MIN_PRICE, MAX_PRICE)

print(gift)