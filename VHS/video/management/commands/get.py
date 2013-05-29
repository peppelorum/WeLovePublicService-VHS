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
import time
import requests
from rethinkdb.errors import RqlRuntimeError, RqlDriverError

use_connection()
q = Queue(default_timeout=60*60*10)
current_site = Site.objects.get_current().domain
#callback_url = 'http://%s:%s%s' % (get_config('BROKER_HOST', 'none'), '8000', reverse('ep_callback'))
# callback_url = 'http://localhost:8000%s' % reverse('ep_callback')
callback_url = 'http://vhs.welovepublicservice.se%s' % reverse('ep_callback')
# print callback_url


def getjson(url):
    urlbase = 'http://api.welovepublicservice.se/'
    tmpurl = urlbase + 'v1/episode/?url=%s' % (url)

    req = requests.get(tmpurl)
    allt = req.json()

    return allt

class SvtGet():

    def __init__(self):

        conn = r.connect('localhost', 28015, 'wlps')
        items = r.table('queue').run(conn)
        run = True

        for queued in items:

            url = queued['url']
            episode_exists = r.table('episode').filter(lambda item: item.contains('url')).filter({'url': url}).count().run(conn)

            if int(episode_exists) == 0:
                allt = getjson(url)

                for obj in allt['objects']:
                    r.db('wlps').table('episode').insert(obj).run(conn)

            episode_exists = r.table('episode').filter(lambda item: item.contains('url')).filter({'url': url}).count().run(conn)
            if int(episode_exists) != 0:

                episode = r.table('episode').filter(lambda item: item.contains('url')).filter({'url': url}).nth(0).run(conn)
                r.table('episode').get(episode['id']).update({'state': 2}).run(conn)

                notif_json = {
                    'episode_id': episode['id'],
                    'user_id': int(queued['user_id'])
                }
                exists = int(r.table('notifications').filter(notif_json).count().run(conn))

                if int(exists) == 0:
                    notif_json.update(
                        {
                            'date_added': int(time.time())
                        })

                if hasattr(episode, 'state'):
                    if episode['state'] == 4:
                        notif_json.update(
                            {
                                'torrent_url': get_config('GS_URL', '') % (get_config('BUCKET', ''), episode['title_slug'] + '.mp4?torrent'),
                            }
                        )
                        run = False

                r.table('notifications').insert(notif_json).run(conn)
                r.table('queue').get(queued['id']).delete().run(conn)

            if run:
                result = q.enqueue(download, episode['id'], episode['title_slug'], episode['url'], get_config('SVTGETSAVEFOLDER', os.path.join(get_config('PROJECT_DIR', 'FAILED'), 'episodes')), callback_url)


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.crawl = SvtGet()
        # self.stdout.write('Yay!')

        # self.stdout.write(get_config('SVTGETSAVEFOLDER', 'noo'))




