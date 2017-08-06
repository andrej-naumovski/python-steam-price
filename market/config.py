from utils.proxy_fetcher import ProxyFetcher

proxy_fetcher = ProxyFetcher('23.95.228.165', 'andrej', 'andrejnaumovski', 'steam')

API = 'https://api.steamapi.io/market/prices/'
API_KEY = 'cfa4f13d2fac6b5328f2ae1c80206f3f'
APP_IDS = {
    'csgo': 730,
    'dota2': 570
}
STEAM_API_URL = 'http://steamcommunity.com/market/listings/'
PROXY_LIST = proxy_fetcher.fetch_proxy_list()
print(PROXY_LIST)
EXPIRED_PROXY_LIST = []