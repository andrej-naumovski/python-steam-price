import MySQLdb


class ProxyFetcher:
    def __init__(self, host, user, password, database):
        self.connection = MySQLdb.Connect(host=host, user=user, passwd=password, db=database, port=3306)
        self.cursor = self.connection.cursor()

    def fetch_proxy_list(self):
        self.cursor.execute('SELECT * FROM proxies')
        results = self.cursor.fetchall()
        proxy_list = []
        for row in results:
            proxy_list.append({
                'http': ProxyFetcher.build_proxy_uri(row)
            })
        return proxy_list

    @staticmethod
    def build_proxy_uri(proxy_tuple):
        return proxy_tuple[4] + '://' + proxy_tuple[2] + ':' + str(proxy_tuple[3])
