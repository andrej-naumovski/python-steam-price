import time

from utils.proxy_checker import ProxyChecker
from market.steam_market import SteamMarket
from utils.constants import Game

steam_market = SteamMarket()

item_names = steam_market.get_item_names(Game.CSGO)


def main():
    print(Game.CSGO)
    timer = time.time()
    proxy_check = ProxyChecker("Proxy checker")
    proxy_check.start()
    for item in item_names[:60]:
        price = steam_market.get_item_price(Game.CSGO, item)
        while price is None:
            price = steam_market.get_item_price(Game.CSGO, item)
    timer = time.time() - timer

    print(timer)

if __name__ == '__main__':
    main()
