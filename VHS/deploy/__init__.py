#from __future__ import absolute_import
#from __future__ import with_statement
#
#from fabric.api import run, env, task, require
#
#from celerydeploy import broker
#from celerydeploy import worker
#
#from svtsave.deploy.utils import virtualenv, import_celeryconfig
#
#
#try:
#    print 2
#    conf = import_celeryconfig()
#    print conf
#except ImportError:
#    print 3
#    pass
#else:
#    print 4
#    if hasattr(conf, 'RQ_DEPLOY_PATH'):
#        env['celery_path'] = conf.RQ_DEPLOY_PATH
#    if not env.hosts and hasattr(conf, 'RQ_DEPLOY_PATH'):
#        env['hosts'] = conf.CELERY_DEPLOY_HOSTS