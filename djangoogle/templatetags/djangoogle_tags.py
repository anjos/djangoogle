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

@register.inclusion_tag('djangoogle/picasaweb_last.html')
def last_album():
  account = PicasawebAccount.objects.all()
  obj = None
  try:
    for a in account:
      if not obj: obj = a.last
      elif obj < a.last: obj = a.last
  except socket.gaierror:
    pass #working offline?
  return {'lastalbum': obj, 'MEDIA_URL': settings.MEDIA_URL}

@register.inclusion_tag('djangoogle/calendar_next.html')
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

