from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'api', 'svtplayapi.urls', name='api'),
    host(r'sys', 'core.urls.sys', name='beta'),
    host(r'www', 'core.urls.www', name='www'),
 )