from django.core.management.base import BaseCommand, CommandError
# from models import Show, Episode, Type

import os
from itertools import chain
from video.tasks import download
from annoying.functions import get_config
from rq import Queue, use_connection
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site

import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError, RqlDriverError

use_connection()
q = Queue(default_timeout=60*60*10)
current_site = Site.objects.get_current().domain
#callback_url = 'http://%s:%s%s' % (get_config('BROKER_HOST', 'none'), '8000', reverse('ep_callback'))
callback_url = 'http://localhost:8001%s' % reverse('ep_callback')
print callback_url

class SvtGet():

    def __init__(self):

        conn = r.connect('localhost', 28015, 'wlps')


        items = r.table('episode').filter(lambda item: item.contains('state')).filter({'state': 1}).run(conn)

        for episode in items:

            # print episode
            r.table('episode').get(episode['id']).update({'state': 2}).run(conn)
            # print episode


            result = q.enqueue(download, episode['id'], episode['title_slug'], episode['url'], get_config('SVTGETSAVEFOLDER', os.path.join(get_config('PROJECT_DIR', 'FAILED'), 'episodes')), callback_url)



        # self.episodes = Episode.objects.filter(state=0, http_status=200).exclude(show__profile=None)
        # self.episodesPreqeued = Episode.objects.filter(state=4, http_status=200)
        # result_list = list(chain(self.episodes, self.episodesPreqeued))
        #
        # for episode in result_list:
        #     print 'GETTING: ', str(episode.id)
        #     print 'URL: ', str(episode.url)
        #
        #     episode.state = 1
        #     episode.save()
        #
        #     result = q.enqueue(download, episode.id, episode.title_slug, episode.url, get_config('SVTGETSAVEFOLDER', os.path.join(get_config('PROJECT_DIR', 'FAILED'), 'episodes')), callback_url)
            #
##            break

class Command(BaseCommand):

    def handle(self, *args, **options):
        if args != ():
            episode = Episode.objects.get(id=args[0])
            print 'GETTING: ', str(episode.id)
            print 'URL: ', str(episode.url)
            episode.state = 1
            episode.save()
            # result = q.enqueue(download, episode.id, episode.title_slug, episode.url, get_config('SVTGETSAVEFOLDER', os.path.join(get_config('PROJECT_DIR', 'FAILED'), 'episodes')), callback_url)
        else:
            self.crawl = SvtGet()
            self.stdout.write('Yay!')

        self.stdout.write(get_config('SVTGETSAVEFOLDER', 'noo'))




