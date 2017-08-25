import json

import arrow

from .config import API, API_KEY, STEAM_API_URL, PROXY_LIST, STEAM_IMAGE_URL, STEAM_HISTORY_URL
import requests
from bs4 import BeautifulSoup
import numpy
import time
import random
import math
from models.item import *
from utils.constants import Csgo
import uuid
import logging
import re

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')


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

    def get_base_item_info(self, appid, item_name):
        url = SteamMarket.build_steam_url(appid, item_name)
        success = False
        while not success:
            try:
                response = requests.get(url, proxies=self.proxies, timeout=0.8)
                success = True
            except:
                logger.debug('Item %s first call failure - proxy %s failed', item_name, self.proxies['http'])
                self.proxies = random.choice(PROXY_LIST)
                success = False

        res_json = None
        while res_json is None:
            if not success:
                self.proxies = random.choice(PROXY_LIST)
                second_success = False
                while not second_success:
                    try:
                        response = requests.get(url, proxies=self.proxies, timeout=0.8)
                        second_success = True
                    except:
                        self.proxies = random.choice(PROXY_LIST)
                        logger.debug('Item %s second call failure - proxy %s failed', item_name, self.proxies['http'])
                        second_success = False
            while response.status_code < 200 or response.status_code >= 300:
                logger.debug('Item %s second call error response - status %d', item_name, response.status_code)
                self.proxies = random.choice(PROXY_LIST)
                success = False
                while not success:
                    try:
                        response = requests.get(url, proxies=self.proxies, timeout=0.8)
                        success = True
                    except:
                        logger.debug('Item %s third call failure - proxy %s failed', item_name, self.proxies['http'])
                        self.proxies = random.choice(PROXY_LIST)
                        success = False
            try:
                res_json = response.json()
            except ValueError:
                success = False
                logger.debug('Failed parsing, invalid JSON, response status %d', response.status_code)
                res_json = None
        return res_json

    def get_price_history(self, appid, item_name):
        url = SteamMarket.build_price_history_url(appid, item_name)
        logger.debug('Price history URL is %s', url)
        success = False
        while not success:
            try:
                response = requests.get(url, proxies=self.proxies)
                success = True
            except:
                logger.debug('Item %s price history first call failure - proxy %s failure', item_name, self.proxies['http'])
                self.proxies = random.choice(PROXY_LIST)
                success = False
        res_content = None
        while res_content is None:
            if not success:
                self.proxies = random.choice(PROXY_LIST)
                second_success = False
                while not second_success:
                    try:
                        response = requests.get(url, proxies=self.proxies, timeout=0.8)
                        second_success = True
                    except:
                        self.proxies = random.choice(PROXY_LIST)
                        logger.debug('Item %s price history second call failure - proxy %s failed', item_name, self.proxies['http'])
                        second_success = False
            while response.status_code < 200 or response.status_code >= 300:
                logger.debug('Item %s price history second call error response - status %d', item_name, response.status_code)
                self.proxies = random.choice(PROXY_LIST)
                success = False
                while not success:
                    try:
                        response = requests.get(url, proxies=self.proxies, timeout=0.8)
                        success = True
                    except:
                        logger.debug('Item %s price history third call failure - proxy %s failed', item_name, self.proxies['http'])
                        self.proxies = random.choice(PROXY_LIST)
                        success = False
            soup = BeautifulSoup(response.content, 'html.parser')
            data = soup.find_all('script')[-1].string

            pattern = re.compile('line1=(.*?);')
            search = pattern.search(data)
            if search is None:
                logger.debug('Item %s price history does not exist', item_name)
                res_content = None
            res_content = json.loads(search.groups()[0])

        return res_content

    def get_item_details(self, appid, item_name):
        res_json = self.get_base_item_info(appid, item_name)
        logger.debug('Passed res_json')
        res_price_history = self.get_price_history(appid, item_name)
        logger.debug('Passed res_price_history')
        prices = SteamMarket.get_parsed_html_price_array(res_json['results_html'])
        price = 0

        res_price_history.reverse()

        past_day = []
        seven_days = []
        thirty_days = []

        today_date = arrow.now()

        for listing in res_price_history:
            date = arrow.get(listing[0], 'MMM D YYYY')
            delta = today_date - date
            if delta.days <= 1:
                past_day.append(listing[1])
                seven_days.append(listing[1])
                thirty_days.append(listing[1])
            elif delta.days <= 7:
                seven_days.append(listing[1])
                thirty_days.append(listing[1])
            elif delta.days <= 30:
                thirty_days.append(listing[1])

        if len(past_day) == 0:
            past_day.append(0)
            seven_days.append(0)
            thirty_days.append(0)

        avg_24h_raw = sum(past_day) / len(past_day)
        avg_7d_raw = sum(seven_days) / len(seven_days)
        avg_30d_raw = sum(thirty_days) / len(thirty_days)

        avg_24h = float('{0:.2f}'.format(avg_24h_raw))
        avg_7d = float('{0:.2f}'.format(avg_7d_raw))
        avg_30d = float('{0:.2f}'.format(avg_30d_raw))

        avg_daily = len(thirty_days) / 30

        item = None

        item_assets = res_json.get('assets')

        if item_assets is None:
            logger.debug('Bad JSON, no item assets for item %s', item_name)
            return None

        asset = None

        try:
            item_assets = item_assets[str(appid)]['2']
            asset = next(iter(item_assets.values()))
        except:
            return None


        image_url = STEAM_IMAGE_URL + asset['icon_url']

        if len(prices) > 0:
            price = numpy.nanmedian(prices)

        if appid == Game.CSGO:
            exterior = None
            item_description = None
            item_rarity = None

            item_desc_value = asset['descriptions'][0]['value']

            if item_desc_value.startswith('Exterior'):
                exterior = item_desc_value.split(':')[-1].strip()
                item_description = asset['descriptions'][2]['value']
                item_type = asset['type'].split()
                if item_type[0].isalpha():
                    item_rarity = item_type[0]
                else:
                    item_rarity = item_type[1]
            else:
                exterior = asset['type'].split(' ')[-1]
                item_description = item_desc_value
                item_rarity = ''.join(asset['type'].split()[:-1])

            item = None

            try:
                item = ItemCsgo.objects().filter(market_name=item_name)
                item.if_exists().update(
                    current_price=price,
                    avg_7_days=avg_7d,
                    avg_7_days_raw=avg_7d_raw,
                    avg_30_days=avg_30d,
                    avg_30_days_raw=avg_30d_raw,
                    num_sales_24hrs=len(past_day),
                    num_sales_7days=len(seven_days),
                    num_sales_30days=len(thirty_days),
                    avg_daily_volume=avg_daily
                )
                logger.info('Item exists: %s', item.market_name)
            except:
                item = ItemCsgo.create(
                    id=uuid.uuid4(),
                    market_name=item_name,
                    current_price=price,
                    image_url=image_url,
                    exterior=exterior,
                    description=item_description,
                    rarity=item_rarity,
                    avg_7_days=avg_7d,
                    avg_7_days_raw=avg_7d_raw,
                    avg_30_days=avg_30d,
                    avg_30_days_raw=avg_30d_raw,
                    num_sales_24hrs=len(past_day),
                    num_sales_7days=len(seven_days),
                    num_sales_30days=len(thirty_days),
                    avg_daily_volume=avg_daily
                )
                logger.info('Item did not exist: %s', item.market_name)

        logger.info('%s price: %.4f', item_name, price)
        return item

    @staticmethod
    def build_steam_url(appid, item_name):
        return STEAM_API_URL + str(appid) + '/' + item_name + '/render?currency=1'

    @staticmethod
    def build_price_history_url(appid, item_name):
        return '{}{}/{}'.format(STEAM_HISTORY_URL, str(appid), item_name)

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
        return float(price_str[1:])
