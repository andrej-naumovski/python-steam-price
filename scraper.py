import time
from market.steam_market import SteamMarket
from utils.constants import Game
from market.worker import Worker
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine import connection
from models.item import ItemCsgo, Item, ItemDota2
import sys

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
    set_cassandra_hosts(['127.0.0.1'])
    set_cassandra_keyspace('scraper')
    connection.setup(cassandra_hosts, cassandra_keyspace_name, protocol_version=3)
    sync_table(Item)
    sync_table(ItemCsgo)
    sync_table(ItemDota2)
    timer = time.time()
    segment = int(len(item_names) / 8)
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


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python3.6 scraper.py <game>')
        sys.exit(2)
    main(sys.argv[1:])
