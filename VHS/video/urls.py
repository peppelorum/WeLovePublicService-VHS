

from django.conf.urls import patterns, url, include
from django.views.generic import RedirectView

# from video import views

urlpatterns = patterns('',

    url(r'^get/$', 'video.views.get', name='get'),
    url(r'^callback/$', 'video.views.callback', name='ep_callback'),
    url(r'^feed/(?P<key>[a-z0-9]+)/$', 'video.views.rss', name='rss'),
    url(r'$', 'video.views.start', name='start'),

    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'template_name': 'registration/logout.html'}, name='logout'),
)
