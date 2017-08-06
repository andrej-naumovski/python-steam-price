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
    print((len(item_names) / 12) * 12)
    segment = int(len(item_names) / 12)
    workers = []
    for i in range(0, 12):
        if i < 11:
            workers.append(Worker('worker ' + str(i + 1), Game.CSGO, item_names[i * segment:(i+1) * segment]))
        else:
            workers.append(Worker('worker 12', Game.CSGO, item_names[i * segment:len(item_names)]))
    for i in range(0, 12):
        workers[i].start()
    for i in range(0, 12):
        workers[i].join()
    timer = time.time() - timer
    print(timer)

if __name__ == '__main__':
    main()
