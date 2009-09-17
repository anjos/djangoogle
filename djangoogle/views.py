#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Created by Andre Anjos <andre.dos.anjos@cern.ch>
# Thu 20 Nov 11:41:27 2008 

"""Specialized views for google apps.
"""

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.conf import settings

from djangoogle.models import *

import time
import datetime
import locale
import socket

populate_defaults()

def set_locale(request):
  try:
    # we try to set the current locale to something that is better
    newloc = locale.normalize(request.LANGUAGE_CODE.replace('-','_')+'.utf8')
    locale.setlocale(locale.LC_ALL, newloc)
  except locale.Error:
    # we simply ignore otherwise, and leave it be
    pass

def view_albums(request, id=None):
  """Gives an overview of the whole available gallery"""

  if not id:
    account = PicasawebAccount.objects.all()
    owner = None
  else:
    account = PicasawebAccount.objects.filter(id=id)
    owner = account[0].email
    
  entries = []

  try:
    for a in account: 
      entries += a.sorted
    entries = sorted(entries, reverse=True)
  except socket.gaierror:
    pass #working offline?

  paginator = Paginator(entries, settings.DJANGOOGLE_ALBUMS_PER_PAGE)

  # Make sure page request is an int. If not, deliver first page.
  try: page = int(request.GET.get('page', '1'))
  except ValueError: page = 1

  # If page request (9999) is out of range, deliver last page of results.
  try: now = paginator.page(page)
  except (EmptyPage, InvalidPage): now = paginator.page(paginator.num_pages)

  return render_to_response('djangoogle/picasaweb_gallery.html', 
                            {'objects': now, 
                             'owner': owner},
                            context_instance=RequestContext(request))

def view_album(request, id, index):
  """Returns a specific album, in slideshow view."""

  account = PicasawebAccount.objects.get(id=id)
  try:
    album = account.sorted[int(index)]
  except socket.gaierror:
    album = None
    pass #working offline?

  return render_to_response('djangoogle/picasaweb_slideshow.html', 
                            {
                              'object': album,
                            },
                            context_instance=RequestContext(request))

def view_videos(request, id=None):
  """Gives an overview of the whole available video gallery"""

  if not id:
    playlists = YouTubePlayList.objects.all()
  else:
    playlists = [YouTubePlayList.objects.get(id=id)]

  entries = []

  try:
    for p in playlists: entries += p.sorted
  except socket.gaierror:
    pass #working offline?
  entries.sort(reverse=True)

  paginator = Paginator(entries, settings.DJANGOOGLE_VIDEOS_PER_PAGE)

  # Make sure page request is an int. If not, deliver first page.
  try: page = int(request.GET.get('page', '1'))
  except ValueError: page = 1

  # If page request (9999) is out of range, deliver last page of results.
  try: now = paginator.page(page)
  except (EmptyPage, InvalidPage): now = paginator.page(paginator.num_pages)

  return render_to_response('djangoogle/youtube_gallery.html', 
                            {'objects': now,}, 
                            context_instance=RequestContext(request))

def view_video(request, id, index):
  """Shows a single video"""
    
  playlist = YouTubePlayList.objects.get(id=id)
  try:
    object = playlist.sorted[int(index)] 
  except socket.gaierror:
    pass #working offline?

  return render_to_response('djangoogle/youtube_video.html', 
                            {'object': object,}, 
                            context_instance=RequestContext(request))

def view_calendar(request):
  """Gives an overview of the whole calendar"""

  accounts = Calendar.objects.all()
  entries = []
  last_update = None
  try:
    for a in accounts:
      entries.extend(a.sorted)
      if not last_update: last_update = a.updated
      elif last_update < a.updated: last_update = a.updated
    entries = sorted(entries)
  except socket.gaierror:
    pass #working offline?

  return render_to_response('djangoogle/calendar_entries.html', 
                            {
                             'updated': last_update,
                             'entries': sorted(entries),
                            },
                            context_instance=RequestContext(request))
