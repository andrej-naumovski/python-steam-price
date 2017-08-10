import threading
from market.steam_market import SteamMarket


class Worker(threading.Thread):
    def __init__(self, id, appid, item_list):
        threading.Thread.__init__(self)
        self.id = id
        self.appid = appid
        self.items = item_list
        self.market = SteamMarket()

    def run(self):
        print('Thread with id ' + self.id + ' started')
        for item in self.items:
            price = None
            while price is None:
                print('Thread ' + self.id)
                price = self.market.get_item_details(self.appid, item)
        print('Thread with id ' + self.id + ' finished')
