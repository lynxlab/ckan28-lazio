import os
import sys
import hashlib

activate_this = os.path.join('/opt/opendata/ckan/ckan28-lazio/datapusher/bin/activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

import ckanserviceprovider.web as web
os.environ['JOB_CONFIG'] = '/opt/opendata/ckan/ckan28-lazio/datapusher/etc/datapusher_settings.py'
web.init()

import datapusher.jobs as jobs

application = web.app


