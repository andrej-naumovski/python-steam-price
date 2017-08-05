from .config import API, API_KEY, STEAM_API_URL, PROXY_LIST, EXPIRED_PROXY_LIST
import requests
from bs4 import BeautifulSoup
import numpy
import time


class SteamMarket:
    def __init__(self):
        self.proxies = {
            'http': 'http://173.224.218.59:80'
        }
        self.item_dict = None

    def get_item_names(self, appid):
        url = API + str(appid) + '?key=' + API_KEY
        print(url)
        response = requests.get(url)
        if 200 <= response.status_code < 300:
            self.item_dict = response.json()
        else:
            print('Error getting response. Status code: ' + str(response.status_code))
            return None
        item_names = []
        for item in self.item_dict:
            item_names.append(item)
        return item_names

    def get_item_price(self, appid, item_name):
        url = SteamMarket.build_steam_url(appid, item_name)
        response = requests.get(url, self.proxies)
        while response.status_code < 200 or response.status_code >= 300:
            if len(PROXY_LIST) == 0:
                print('No more proxies left. Try again later.')
                return None
            EXPIRED_PROXY_LIST.append({
                'proxy': self.proxies['http'],
                'timestamp': time.time()
            })
            self.proxies['http'] = PROXY_LIST.pop(0)
            response = requests.get(url, self.proxies)
        res_json = response.json()
        prices = SteamMarket.get_parsed_html_price_array(res_json['results_html'])
        price = 0
        if len(prices) > 0:
            price = numpy.nanmedian(prices)
        print(item_name + ': ' + str(price))
        return price

    @staticmethod
    def build_steam_url(appid, item_name):
        return STEAM_API_URL + str(appid) + '/' + item_name + '/render?currency=3'

    @staticmethod
    def get_parsed_html_price_array(listings):
        soup = BeautifulSoup(listings, 'html.parser')
        prices = soup.find_all('span', 'market_listing_price market_listing_price_with_fee')
        prices_array = []
        for price in prices:
            prices_array.append(SteamMarket.parse_item_price(price.contents[0]))
        if len(prices_array) > 0:
            return numpy.array(prices_array)
        return numpy.empty(shape=(0, 0))

    @staticmethod
    def parse_item_price(price_str):
        price_str = price_str.strip().replace(',', '.').replace(' ', '')
        if price_str[-2] == '-':
            return float(price_str.split('.')[0])
        return float(price_str[:-1])
