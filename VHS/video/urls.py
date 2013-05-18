

from django.conf.urls import patterns, url, include
from django.views.generic import RedirectView

# from video import views

urlpatterns = patterns('',

    url(r'^get/$', 'video.views.get', name='get'),
    url(r'^callback/$', 'video.views.callback', name='ep_callback'),
    url(r'^stats/$', 'video.views.stats', name='stats'),
    url(r'^feed/(?P<key>[a-z0-9]+)/$', 'video.views.rss', name='rss'),
    url(r'$', 'video.views.start', name='start'),


)
