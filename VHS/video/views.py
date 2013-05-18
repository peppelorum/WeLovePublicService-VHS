# Create your views here.

import time

from django.shortcuts import render_to_response, HttpResponse, Http404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext

from django.contrib.auth.models import User

# from libs.rwrapper import rwrapper

import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError, RqlDriverError

from annoying.functions import get_config

from models import Profile


@login_required()
def start(request):

    conn = r.connect('localhost', 28015, 'wlps')

    profile = Profile.objects.get(user=request.user)

    notifications = r.table('notifications').eq_join('episode_id', r.table('episode')).order_by(r.asc('date_added')).run(conn)
    # downloaded = r.table('notifications').eq_join('episode_id', r.table('episode')).filter(lambda item: item.contains('torrent_url')).order_by(r.asc('date_added')).run(conn)

    dic = {
        'notifications': notifications,
        'profile': profile
        # 'downloaded': downloaded
    }

    return render_to_response('video/1.html',
                              dic,
                              context_instance=RequestContext(request))


@login_required()
def get(request):
    url = request.GET.get('url')

    conn = r.connect('localhost', 28015, 'wlps')

    # items = r.db('wlps').table('episode').filter(lambda item: item.contains('state')).filter({'state': 2}).run()
    #
    # for a in items:
    #     print a


    try:
        item = r.table('episode').filter(lambda item: item.contains('url')).filter({'url': url}).nth(0).run(conn)

        r.table('episode').get(item['id']).update({'state': 1}).run(conn)

        notif_json = {
            'episode_id': item['id'],
            'user_id': int(request.user.id)
        }

        exists = int(r.table('notifications').filter(notif_json).count().run(conn))

        if exists == 0:
            notif_json.update({'date_added': int(time.time())})
            r.table('notifications').insert(
                notif_json
            ).run(conn)

    except ValueError as err:
        # item = 's'
        print err
        pass

    except RqlRuntimeError as err:
        # item = 's'
        print err
        raise Http404

        pass

    return redirect('start')


def stats(request):
    conn = r.connect('localhost', 28015, 'wlps')

    notifications = r.table('notifications').eq_join('episode_id', r.table('episode')).run(conn)

    dic = {
        'notifications': notifications
    }

    return render_to_response(
        'video/stats.html',
        dic,
        context_instance=RequestContext(request))


@csrf_exempt
def callback(request):
    req_id = request.POST.get('id')
    key = request.POST.get('key')
    state = int(request.POST.get('state'))

    if key != get_config('CALLBACKKEY', ''):
        return HttpResponse('Nay....')

    conn = r.connect('localhost', 28015, 'wlps')

    item = r.table('episode').get(req_id).run(conn)

    r.table('episode').get(item['id']).update({'state': state}).run(conn)

    if state == 4:

        notif_json = {
            'torrent_url': get_config('GS_URL', '') % (get_config('BUCKET', ''), item['title_slug'] + '.mp4?torrent')
        }

        episodes = r.table('notifications').filter({'episode_id': req_id}).update(notif_json).run(conn)

        for a in episodes:
            print a

    return HttpResponse('Yay!')




def rss(request, key):

    print 'key', key

    conn = r.connect('localhost', 28015, 'wlps')

    user = Profile.objects.get(unique=key)

    # notifications = r.table('notifications').filter({'user_id': user.id}).run(conn)

    notifications = r.table('notifications').eq_join('episode_id', r.table('episode')).run(conn)

    print user

    dic = {
        'notifications': notifications
    }

    return render_to_response('video/rss.html', dic, content_type='application/rss+xml')

#
# from django.contrib.syndication.views import Feed
# from notifications.models import Notification
#
# class LatestEntriesFeed(Feed):
#     title = "WLPS Your personal torrent feed"
#     link = "http://sys.welovepublicservice.se/"
#     # description = ""
#
#     # def get_object(self, request, key):
#     #     return get_object_or_404(Profile, unique=key)
#
#     def items(self, obj):
#         return Notification.objects.filter(recipient=obj.user, actor_content_type__name='episode')
#
#     def item_title(self, item):
#         # return item.actor
#         return '%s - %s' % (item.actor.show, item.actor)
#
#     def item_description(self, item):
#         return item.description
#         # return '%s - %s' % (item.show, item.description)
#
#     def item_link(self, item):
#         try:
#             return item.actor.episode_link_torrent()
#         except:
#             pass