from utils.proxy_fetcher import ProxyFetcher

proxy_fetcher = ProxyFetcher('23.95.228.165', 'scraper', 'scraper123@', 'steam')

API = 'https://api.steamapi.io/market/prices/'
API_KEY = '25aed365820ec0b2600a2f41a32e8049'
APP_IDS = {
    'csgo': 730,
    'dota2': 570
}
STEAM_API_URL = 'http://steamcommunity.com/market/listings/'
STEAM_HISTORY_URL = 'http://steamcommunity.com/market/listings/'
PROXY_LIST = proxy_fetcher.fetch_proxy_list()
CHECKED_ITEMS = 0

STEAM_IMAGE_URL = 'http://steamcommunity-a.akamaihd.net/economy/image/'
