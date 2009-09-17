#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Created by Andre Anjos <andre.dos.anjos@cern.ch>
# Qua 16 Set 2009 17:51:23 CEST 

"""A few global settings for this package
"""

from pytz import timezone
from os import environ

defaults = {}
defaults['DJANGOOGLE_TIMEZONE'] = timezone('UTC')

# If the user has defined an environment variable for the timezone, we use it
if environ.has_key('TZ'): 
  defaults['DJANGOOGLE_TIMEZONE'] = timezone(environ['TZ'])

# Controls how many albums per page to see
defaults['DJANGOOGLE_ALBUMS_PER_PAGE'] = 10

# Controls how many videos per page to see
defaults['DJANGOOGLE_VIDEOS_PER_PAGE'] = 4

