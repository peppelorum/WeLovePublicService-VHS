
import os
from rq_settings import *

os.system('rqworker -H %s -p %s' % (BROKER_HOST, BROKER_PORT))