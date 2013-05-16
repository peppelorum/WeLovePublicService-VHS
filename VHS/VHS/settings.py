# Django settings for svtsave project.

import dj_database_url
import os, sys
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
SETTINGS_DIR = os.path.dirname(__file__)
ENV_FILE = 'env.py'

try:
    import env
except:
    print 'ENV_FILE is missing'

try:
    BROKER_HOST = os.environ['BROKER_HOST']
    BROKER_PORT = os.environ['BROKER_PORT']
    # SESSION_COOKIE_DOMAIN = os.environ['SESSION_COOKIE_DOMAIN']
    GS_KEY = os.environ['GS_KEY']
    GS_SECRET = os.environ['GS_SECRET']
except IndexError:
    print '*********************************************************'
    print 'You need to define GS_KEY and GS_SECRET as env variables.'
    print '*********************************************************'
except KeyError as inst:
    print '*********************************************************'
    print 'Some thing is missing in env.py: '
    print inst
    print '*********************************************************'

BUCKET = 'wlps'
GOOGLE_STORAGE = 's3'
GS_URL = 'https://s3-eu-west-1.amazonaws.com/%s/%s'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Peppe', 'pepplorum+wlpsdebug@gmail.com'),
)

INTERNAL_IPS = ('127.0.0.1',)

MANAGERS = ADMINS

DATABASES = {'default': dj_database_url.config(default='sqlite:////%s' % (os.path.join(PROJECT_DIR, 'test.db'), ))}
#
# CACHES = {
#     'default': {
#         'BACKEND': 'johnny.backends.redis.RedisCache',
#         'LOCATION': '%s:%s' % ('localhost', '6379'),
#         'JOHNNY_CACHE': True,
#         'OPTIONS': {
#             'DB': 1,
#             #'PASSWORD': redis_url.password,
#             }
#     }
# }

JOHNNY_MIDDLEWARE_KEY_PREFIX='jc_wlps'


PROXIED_SITE_TEMPLATE = """\
server {
    listen %(port)s;
    server_name %(server_name)s;

    gzip_vary on;

    # path for static files
    #root %(docroot)s;

    location /static/  {
        autoindex    on;
        alias %(docroot)s;
    }


    try_files $uri @proxied;

    location @proxied {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_pass %(proxy_url)s;
    }

    access_log /var/log/nginx/%(server_name)s.log;
}
"""


#BROKER_URL = 'redis://guest:guest@localhost:6379/'
#BROKER_URL = 'redis://localhost:6379/'
#BROKER_URL = 'amqp://hoj:hoj@10.211.55.8:5672/tji/'

TIME_ZONE = 'Europe/Stockholm'
LANGUAGE_CODE = 'sv-se'

SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True

MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')
MEDIA_URL = ''
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(SETTINGS_DIR, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'y=s4l^5aw8x-@)$g26t%0&amp;t82#5f*seo4o&amp;gh7ivo!67ia&amp;29j'

# List of callables that know how to import templates from various sources.

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',

    'apptemplates.Loader',
    #     'django.template.loaders.eggs.Loader',
)
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
#    'core.middleware.SubdomainsMiddleware',
#     'django_hosts.middleware.HostsMiddleware',
    'VHS.utils.middlewares.rDBMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # 'johnny.middleware.LocalStoreClearMiddleware',
    # 'johnny.middleware.QueryCacheMiddleware',



    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

# SESSION_COOKIE_DOMAIN = 'localhost' if not DEBUG else '.local'

ROOT_URLCONF = 'VHS.urls'
# ROOT_HOSTCONF = 'VHS.hosts'
# DEFAULT_HOST = 'www'

LOGIN_REDIRECT_URL = '/'

NOTIFY_USE_JSONFIELD=True

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'VHS.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.

    os.path.join(SETTINGS_DIR, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'core',
    'south',
    'django_extensions',
    'annoying',
    'bootstrap_toolkit',
    'gunicorn',
    'debug_toolbar',
    # 'django_hosts',
    # 'tastypie',
    'notifications',
    'video',
    # 'svtplayapi',
    # 'tastypie_swagger',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
)

# TASTYPIE_SWAGGER_API_MODULE = 'svtplayapi.urls.v1_api'

TEMPLATE_CONTEXT_PROCESSORS = ("django.contrib.auth.context_processors.auth",
                               "django.core.context_processors.debug",
                               "django.core.context_processors.i18n",
                               "django.core.context_processors.media",
                               "django.core.context_processors.static",
                               "django.core.context_processors.tz",
                               "django.contrib.messages.context_processors.messages",
                               'django.core.context_processors.request')


SVTGETSAVEFOLDER = os.path.join(ROOT_DIR, 'episodes')
SVTGETSAVEFOLDER = 'episodes'

#print SVTGETSAVEFOLDER


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

#BROKER_HOST = '10.211.55.2'

RQ_DEPLOY_PATH = 'ost'
RQ_IMPORTS = (
    ['video/tasks.py', 'video/tasks.py'],
    ['libs/*.py', 'libs/'],
    ['deploy/startrq.py', 'startrq.py'],

)

RQ_SETTINGS_NEEDED = (
    'GS_KEY',
    'GS_SECRET',
    'GOOGLE_STORAGE',
    'BUCKET',
    'BROKER_HOST',
    'BROKER_PORT',
    'CALLBACKKEY'
)
RQ_PIP = ('requests', 'BeautifulSoup', 'simplejson', 'django-annoying', 'boto', 'rq', )
DJANGO_SETTINGS_MODULE = 'VHS.settings'


try:
    from local_settings import *
except:
    pass