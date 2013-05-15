__author__ = 'peppe'

import rethinkdb as r


def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance


@singleton
class rDBMiddleware(object):
    connection = None

    def __init__(self):
        if self.connection is None:
            self.connection = r.connect(host='localhost', port=28015, db='wlps').repl()

    def process_request(self, request):
        return None