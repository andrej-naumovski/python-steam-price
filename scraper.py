import time
from market.steam_market import SteamMarket
from utils.constants import Game
from market.worker import Worker
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine import connection
from models.item import ItemCsgo, Item, ItemDota2
from market.history_worker import HistoryWorker
import sys
import market.config

steam_market = SteamMarket()

cassandra_hosts = []
cassandra_keyspace_name = ''


def set_cassandra_hosts(hosts: list):
    global cassandra_hosts
    cassandra_hosts = hosts


def set_cassandra_keyspace(keyspace: str):
    global cassandra_keyspace_name
    cassandra_keyspace_name = keyspace


def main(argv):
    game = None
    if argv[0] == 'csgo':
        game = Game.CSGO
    elif argv[0] == 'dota2':
        game = Game.DOTA2
    item_names = steam_market.get_item_names(game)
    print('Number of items is %d' % len(item_names))
    set_cassandra_hosts(['127.0.0.1'])
    set_cassandra_keyspace('scraper')
    connection.setup(cassandra_hosts, cassandra_keyspace_name, protocol_version=3)
    sync_table(Item)
    sync_table(ItemCsgo)
    sync_table(ItemDota2)
    timer = time.time()
    segment = int(len(item_names) / 8)
    print('Segment size is %d' % segment)
    workers = []
    for i in range(0, 8):
        if i < 7:
            workers.append(Worker('worker ' + str(i + 1), Game.CSGO, item_names[i * segment:(i+1) * segment]))
        else:
            workers.append(Worker('worker 8', Game.CSGO, item_names[i * segment:len(item_names)]))
    for i in range(0, 8):
        workers[i].start()
    for i in range(0, 8):
        workers[i].join()
    print('Number of items %d' % ItemCsgo.objects.count())
    timer = time.time() - timer
    print(timer)
    for i in range(0, 60):
        print('Sleeping %d seconds' % i)
        time.sleep(1)
    workers = []
    market.config.CHECKED_ITEMS = 0
    timer_history = time.time()
    for i in range(0, 8):
        if i < 7:
            workers.append(HistoryWorker('worker ' + str(i + 1), Game.CSGO, item_names[i * segment:(i + 1) * segment]))
        else:
            workers.append(HistoryWorker('worker 8', Game.CSGO, item_names[i * segment:len(item_names)]))
    for i in range(0, 8):
        workers[i].start()
    for i in range(0, 8):
        workers[i].join()
    timer_history = time.time() - timer_history
    print(timer_history)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python3.6 scraper.py <game>')
        sys.exit(2)
    main(sys.argv[1:])
