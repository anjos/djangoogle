#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Created by Andre Anjos <andre.dos.anjos@cern.ch>
# Ter 01 Abr 2008 17:44:41 CEST 

from django.template import Library
from django.template.defaultfilters import stringfilter
from djangoogle.models import *
import time

register = Library()

@register.filter
@stringfilter
def gd_date(value, arg):
  """Formats a Google Data style date into the format you want"""
  try:
    return time.strftime(str(arg), 
             time.strptime(value.split('.')[0], '%Y-%m-%dT%H:%M:%S'))
  except:
    return value

@register.filter
@stringfilter
def str2int(value):
  """Returns the value as integer"""
  try:
    return int(value)
  except:
    return value

@register.filter
@stringfilter
def getitem(value, arg):
  """Gets an item from a dictionary"""
  try: 
    return value[arg]
  except:
    return ''

@register.filter("special_pagination")
def special_pagination(paginator):
  around = 3 # number of pages around the current one to show
  pages = range(paginator.number - around, paginator.number + around + 1) 
  pages = [k for k in pages if k > 0 and k <= paginator.paginator.num_pages]
  if pages[0] > 1: 
    if pages[0] > 2: pages.insert(0, False)
    pages.insert(0, 1)
  if pages[-1] < paginator.paginator.num_pages:
    if pages[-1] < (paginator.paginator.num_pages - 1): pages.append(False)
    pages.append(paginator.paginator.num_pages)
  return pages

@register.filter
def is_album(value):
  """Says if this object is a PicasaWeb album or not."""
  return isinstance(value, PicasaWebAlbum)

@register.filter
def is_video(value):
  """Says if this object is an YouTube video or not."""
  return isinstance(value, YouTubeVideo)

@register.filter
def is_even(value):
  """Says if the value is even"""
  return value%2 == 0
