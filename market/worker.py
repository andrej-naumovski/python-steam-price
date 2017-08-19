import threading
from market.steam_market import SteamMarket
import logging
import market.config

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')

class Worker(threading.Thread):
    def __init__(self, id, appid, item_list):
        threading.Thread.__init__(self)
        self.id = id
        self.appid = appid
        self.items = item_list
        self.market = SteamMarket()

    def run(self):
        logger.info('Thread started')
        for item in self.items:
            price = self.market.get_item_details(self.appid, item)
            market.config.CHECKED_ITEMS += 1
            logger.info("Number of passed items: %d", market.config.CHECKED_ITEMS)
        logger.info('Thread finished')
