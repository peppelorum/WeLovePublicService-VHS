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

    try:
        r.db('wlps').table_create('queue').run()
    except RqlRuntimeError:
        pass


class Command(BaseCommand):

    def handle(self, *args, **options):
        index()