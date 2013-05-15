# -*- coding: utf-8 -*-

#from celery import task
#from models import Show, Episode
from libs.svtget import Pirateget

#@task()
#def add(x, y):
#    return x + y

#@task()
def download(pk, title, url, folder, callback_url):

    print 'pk', pk
    # print 'title', unicode(title)
    print 'url', url
    print 'folder', folder
    print 'callback_url', callback_url
    obj = Pirateget()
#    obj.checkReqs()
#    episode.state = 1
#    episode.save()
    obj.run(pk, title, url, folder, callback_url)


