from .config import API, API_KEY, STEAM_API_URL, PROXY_LIST, EXPIRED_PROXY_LIST
import requests
from bs4 import BeautifulSoup
import numpy
import time
import random


class SteamMarket:
    def __init__(self):
        self.proxies = random.choice(PROXY_LIST)
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
        success = False
        print('Here')
        while not success:
            try:
                response = requests.get(url, proxies=self.proxies, timeout=0.8)
                success = True
            except:
                print('First call exception')
                self.proxies = random.choice(PROXY_LIST)
                success = False
        print('Here2')
        res_json = None
        while res_json is None:
            print(response.status_code)
            if not success:
                self.proxies = random.choice(PROXY_LIST)
                second_success = False
                while not second_success:
                    try:
                        second_success = True
                        response = requests.get(url, proxies=self.proxies, timeout=0.8)
                    except:
                        self.proxies = random.choice(PROXY_LIST)
                        second_success = False
            while response.status_code < 200 or response.status_code >= 300:
                self.proxies = random.choice(PROXY_LIST)
                print('Current proxy: ' + self.proxies['http'])
                #time.sleep(2)
                success = False
                while not success:
                    try:
                        response = requests.get(url, proxies=self.proxies, timeout=0.8)
                        success = True
                    except:
                        print('Second call exception')
                        self.proxies = random.choice(PROXY_LIST)
                        success = False
            res_json = None
            try:
                res_json = response.json()
            except ValueError:
                success = False
                print(response.text)
                res_json = None
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
        if price_str[:-1] == 'Sold':
            return 0
        return float(price_str[:-1])
