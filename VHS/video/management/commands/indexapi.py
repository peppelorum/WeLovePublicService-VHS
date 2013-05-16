from django.core.management.base import BaseCommand, CommandError

import requests
from rethinkdb.errors import RqlRuntimeError


def index():

    import rethinkdb as r
    r.connect('localhost', 28015).repl()

    try:
        r.db_create('wlps').run()
    except RqlRuntimeError:
        pass

    try:
        r.db('wlps').table_create('episode').run()
    except RqlRuntimeError:
        pass

    try:
        r.db('wlps').table_create('show').run()
    except RqlRuntimeError:
        pass

    try:
        r.db('wlps').table_create('notifications').run()
    except RqlRuntimeError:
        pass

    offset = 0
    limit = 1000
    urlbase = 'http://api.welovepublicservice.se/'

    urlShow = urlbase + 'v1/show/?limit=%d' % limit
    find = False

    while True:
        req = requests.get(urlShow)
        shows = req.json()

        for show in shows['objects']:

            del show['episodes']

            a = r.db('wlps').table('show').insert(show).run()
            url = urlbase + 'v1/episode/?show=%d&limit=%d' % (int(show['id']), limit)

            while True:
                req = requests.get(url)
                allt = req.json()

                for obj in allt['objects']:
                    a = r.db('wlps').table('episode').insert(obj).run()

                if allt['meta']['next'] == None:
                    break
                else:
                    url = urlbase + allt['meta']['next']

        if shows['meta']['next'] == None:
            break
        else:
            urlShow = urlbase + shows['meta']['next']


class Command(BaseCommand):

    def handle(self, *args, **options):
        index()