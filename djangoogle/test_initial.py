#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Created by Andre Anjos <andre.dos.anjos@cern.ch>
# Qua 16 Set 2009 14:55:07 CEST 

"""
"""

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings'

from djangoogle.models import *

# Inserts a few galleries for tests:
example1 = PicasawebAccount(email='irina1005@gmail.com', num_albums=20)
example1.save()

example2 = PicasawebAccount(email='bmcclendon@gmail.com', num_albums=10)
example2.save()

example3 = PicasawebAccount(email='mahaniok@gmail.com', num_albums=0)
example3.save()

# Inserts a few YouTube feeds
yt1 = YouTubePlayList(name='Example 1', list='E49E3B8EE184CF25')
yt1.save()
yt2 = YouTubePlayList(name='Example 2', list='38743EACD21A054C')
yt2.save()

# And a few calendars
cal1 = Calendar(calendar_id='df5gn5s0g0ks4pkpjm1kk0n26428h2d0@import.calendar.google.com')
cal1.save()
cal2 = Calendar(calendar_id='nf89st0pjn6vpmq7t2qda95i9cg9lphm%40import.calendar.google.com')
cal2.save()
