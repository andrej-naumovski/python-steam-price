import threading
import time
from market.config import PROXY_LIST, EXPIRED_PROXY_LIST


class ProxyChecker(threading.Thread):
    def __init__(self, thread_id):
        threading.Thread.__init__(self)
        self.thread_id = thread_id

    def run(self):
        print('Starting thread: ' + self.thread_id)
        check_proxy_timestamp(self.thread_id)
        print('Ending thread: ' + self.thread_id)


def check_proxy_timestamp(thread_id):
    while True:
        i = 0
        if len(EXPIRED_PROXY_LIST) == 0:
            print(thread_id + ': No expired proxies')
        else:
            print('Already expired proxies:')
        for proxy in EXPIRED_PROXY_LIST:
            print(proxy)
            if time.time() - proxy['timestamp'] > 10:
                PROXY_LIST.append(proxy['proxy'])
                EXPIRED_PROXY_LIST.pop(i)
            else:
                i = i + 1
        time.sleep(1)
