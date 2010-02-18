#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Created by Andre Anjos <andre.dos.anjos@cern.ch>
# Seg 16 Mar 2009 18:32:11 CET 

"""Introduces tags to facilitate the placement of "album views"
"""

from django import template
from django.conf import settings
register = template.Library()

from djangoogle.models import *
import socket

@register.inclusion_tag('djangoogle/embed/media_last.html')
def djangoogle_last_media(url=settings.MEDIA_URL):
  return {'MEDIA_URL': url}

@register.inclusion_tag('djangoogle/embed/picasaweb_last.html')
def last_albums(n, media_url=settings.MEDIA_URL):
  account = PicasawebAccount.objects.all()
  entries = []
  try:
    for a in account: 
      entries += a.sorted
    entries = sorted(entries, reverse=True)
  except socket.gaierror:
    pass #working offline?
  return {'objects': entries[:n], 'MEDIA_URL': media_url}

@register.inclusion_tag('djangoogle/embed/youtube_last.html')
def last_videos(n, media_url=settings.MEDIA_URL):
  playlists = YouTubePlayList.objects.all()
  entries = []
  try:
    for p in playlists: entries += p.sorted
  except socket.gaierror:
    pass #working offline?
  entries.sort(reverse=True)
  return {'objects': entries[:n], 'MEDIA_URL': media_url}

@register.inclusion_tag('djangoogle/embed/all_last.html')
def last_all(albums, videos, media_url=settings.MEDIA_URL):
  d = last_albums(albums, media_url)
  d['albums'] = d['objects']
  d.update(last_videos(videos, media_url))
  d['videos'] = d['objects']
  del d['objects']
  return d

@register.inclusion_tag('djangoogle/embed/calendar_next.html')
def next_calendar_item():
  calendars = Calendar.objects.all()
  obj = None
  try:
    for a in calendars:
      if not a.next: continue
      if obj: 
        if a.next < obj: obj = a.next
      else: obj = a.next
  except socket.gaierror:
    pass #working offline?
  return {'object': obj}

@register.inclusion_tag('djangoogle/pagination.html')
def pagination(paginator):
  return {'paginator': paginator}

@register.simple_tag
def picasaweb_slideshow(obj, language, width, height):
  return obj.slideshow_html(language, width, height)

