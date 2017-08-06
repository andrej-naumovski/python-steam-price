import time
from market import config
from utils.proxy_checker import ProxyChecker
from market.steam_market import SteamMarket
from utils.constants import Game
from market.worker import Worker

steam_market = SteamMarket()


def main():
    item_names = steam_market.get_item_names(Game.CSGO)
    timer = time.time()
    # proxy_check = ProxyChecker("Proxy checker")
    # proxy_check.start()
    workers = []
    for i in range(0, 8):
        workers.append(Worker('worker ' + str(i + 1), Game.CSGO, item_names[i * 20:(i+1) * 20]))
    for i in range(0, 8):
        workers[i].start()
    for i in range(0, 8):
        workers[i].join()
    timer = time.time() - timer
    print(timer)

if __name__ == '__main__':
    main()
