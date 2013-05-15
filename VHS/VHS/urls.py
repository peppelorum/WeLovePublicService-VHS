from django.conf.urls import patterns, include, url

# from core.views.sys import EpisodeCallback

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'svtsave.views.home', name='home'),
    url(r'^', include('video.urls')),

    # url(
    #     regex=r"^episode/callback/$",
    #     view=EpisodeCallback,
    #     name="ep_callback",
    # ),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', name='logout'),


)