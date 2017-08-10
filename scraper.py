import time
from market import config
from utils.proxy_checker import ProxyChecker
from market.steam_market import SteamMarket
from utils.constants import Game
from market.worker import Worker
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine import connection
from models.item import ItemCsgo, Item, ItemDota2

steam_market = SteamMarket()

connection.setup(['127.0.0.1'], "scraper", protocol_version=3)

sync_table(Item)
sync_table(ItemCsgo)
sync_table(ItemDota2)


def main():
    item_names = steam_market.get_item_names(Game.CSGO)
    timer = time.time()
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

    print('Number of items %d' % ItemCsgo.objects.count())
    timer = time.time() - timer
    print(timer)


if __name__ == '__scraper__':
    main()
