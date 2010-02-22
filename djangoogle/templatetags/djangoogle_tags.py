#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Created by Andre Anjos <andre.dos.anjos@cern.ch>
# Seg 16 Mar 2009 18:32:11 CET 

"""Introduces tags to facilitate the placement of "album views"
"""

from django import template
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
register = template.Library()

from djangoogle.models import *
import socket

@register.inclusion_tag('djangoogle/embed/media_last.html')
def djangoogle_last_media(): return {}

@register.inclusion_tag('djangoogle/embed/picasaweb_vignette.html')
def picasaweb_vignette(obj, thumb_height, title_trunc):
  return {'obj': obj, 
          'thumb_height': thumb_height, 
          'title_trunc': title_trunc,
         }

@register.inclusion_tag('djangoogle/embed/youtube_vignette.html')
def youtube_vignette(obj, thumb_height, title_trunc, desc_trunc):
  return {'obj': obj, 
          'thumb_height': thumb_height, 
          'title_trunc': title_trunc,
          'desc_trunc': desc_trunc,
         }

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

def last_albums(n):
  account = PicasawebAccount.objects.all()
  entries = []
  try:
    for a in account: 
      entries += a.sorted
    entries = sorted(entries, reverse=True)
  except socket.gaierror:
    pass #working offline?
  return entries[:n]

def last_videos(n):
  playlists = YouTubePlayList.objects.all()
  entries = []
  try:
    for p in playlists: entries += p.sorted
  except socket.gaierror:
    pass #working offline?
  entries.sort(reverse=True)
  return entries[:n] 

@register.inclusion_tag('djangoogle/embed/box.html')
def djangoogle_media_box(nphotos=3, nvideos=1, ncolumns=2, 
    thumb_height=80, title_trunc=5, desc_trunc=8):

  photos = last_albums(nphotos)
  videos = last_videos(nvideos)
  objects = sorted(photos + videos, reverse=True)
  table = [objects[i:(i+ncolumns)] for i in range(0, len(objects), ncolumns)] 
  title = _(u'Latest media')
  if nphotos and not nvideos: title=_(u'Latest photos')
  if nvideos and not nphotos: title=_(u'Latest videos')
  return {
      'objects': table, 
      'title': title,
      'thumb_height': thumb_height,
      'title_trunc': title_trunc,
      'desc_trunc': desc_trunc,
      }

