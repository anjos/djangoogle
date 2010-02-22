from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.utils.translation import string_concat  as _cat
from django.conf import settings

import gdata.photos.service
import gdata.calendar.service
import gdata.youtube.service
import gdata.service
import time
import pytz
import datetime
import urllib
import re

def populate_defaults():
  from django.conf import settings
  from djangoogle.settings import defaults
  for var in defaults.keys():
    if not hasattr(settings, var):
      setattr(settings, var, defaults[var])

populate_defaults()

YOUTUBE_VIDEO_DATA = re.compile('^.*/feeds\/api/videos/[^/]*$')
YOUTUBE_VIDEO_PAGE = re.compile('^.*/watch\?v=[^/]*$')

def get_video_link(l, regexp):
  """Selects the URL that mostly looks like the video main entry."""
  retval = [k.href for k in l if regexp.match(k.href)]
  if len(retval): return retval[0]
  return None

def gd_date(s):
  """Converts a google data date representation into a real date"""
  p = time.strptime(s.split('.')[0], '%Y-%m-%dT%H:%M:%S')[0:6]
  return datetime.datetime(p[0], p[1], p[2], p[3], p[4], p[5], 
      tzinfo=settings.DJANGOOGLE_TIMEZONE)

def outdated(obj):
  """Decides if obj is outdated."""
  if not hasattr(obj, '__updated__'): return True
  return (time.time() - obj.__updated__) > 300 # we update every 5 minutes

class UserInfo:
  """Describes the user info class"""
  def __init__(self, user, nickname, uri, available_items, last_update, feed,
      thumbnail):
    self.user = user
    self.nickname = nickname
    self.uri = uri
    self.available_items = available_items
    self.last_update = last_update
    self.feed = feed
    self.thumbnail = thumbnail
    if self.feed: self.is_valid = True
    else: self.is_valid = False

class PicasaWebAlbum:
  """This is a wrapper to make easier the manipulation of PicasaWeb albums."""

  FlashPlayerTemplate = '<embed type="application/x-shockwave-flash" src="http://picasaweb.google.com/s/c/bin/slideshow.swf" width="%(width)s" height="%(height)s" flashvars="host=picasaweb.google.com&captions=1&hl=%(language)s&feat=flashalbum&RGB=0x000000&feed=%(url)s" pluginspage="http://www.macromedia.com/go/getflashplayer"></embed>'

  def __init__(self, entry, parent):
    """Initialize from Google data feed entry from YouTube."""
    self.entry = entry
    self.author = entry.author[0].name.text
    self.nickname = entry.nickname.text
    self.title = entry.media.title.text
    self.published = gd_date(entry.published.text)
    self.updated = gd_date(entry.updated.text)
    self.thumbnail = entry.media.thumbnail[0]
    self.parent = parent
    self.numphotos = int(entry.numphotos.text)
    self.description = entry.media.description.text
    self.location = entry.location.text
    self.latitude = entry.geo.latitude
    self.longitude = entry.geo.longitude
    self.google_id = entry.id.text
    self.slideshow_url = entry.link[0].href 
    self.slideshow_url += '?alt=rss&kind=photo&hl=%(language)s'
    self.web_url = entry.link[1].href

  def slideshow_html(self, language=settings.LANGUAGE_CODE, width=400, height=267):
    """Returns the flash player embeddeable html for slideshowing."""
    return PicasaWebAlbum.FlashPlayerTemplate % \
        {
         'url': urllib.quote(self.slideshow_url % {'language': language}, ''),
         'language': language,
         'width': width,
         'height': height,
        }

  def _id(self):
    return self.parent.sorted.index(self)

  # dynamic property
  id = property(_id)

  def __cmp__(self, other):
    return cmp(self.published, other.published)

class PicasawebAccount(models.Model):
  """This model describes an user account in picasaweb."""

  email = models.EmailField(_('Picasaweb e-mail'), max_length=256, unique=True,
      help_text=_('Insert the e-mail of a picasaweb user in the form of user@domain'))
  num_albums = models.PositiveSmallIntegerField(\
    _('Number of albums to display'), default=0,
    help_text=_('The special value of 0 (zero) will display all albums'))

  class Meta: 
    verbose_name = _(u'google picasa web account')
    verbose_name_plural = _(u'google picasa web accounts')

  def _cache_userinfo(self):
    """Returns user information, packed in a special object type."""
    if not hasattr(self, '__userinfo__') or not self.__userinfo__ or outdated(self):
      try:
        pws = gdata.photos.service.PhotosService()
        feed = pws.GetUserFeed(user=self.email, limit=0)
        self.__userinfo__ = UserInfo(feed.user.text,
                                     feed.nickname.text,
                                     feed.author[0].uri.text,
                                     feed.total_results.text,
                                     feed.updated.text,
                                     feed.id.text,
                                     feed.thumbnail.text)
        self.__updated__ = time.time()
      except gdata.photos.service.GooglePhotosException:
        self.__userinfo__ = UserInfo('', '', '', '', '', '')
    return self.__userinfo__

  # dynamic property
  userinfo = property(_cache_userinfo)

  def _cache_feed(self):
    if not hasattr(self, '__feed__') or not self.__feed__ or outdated(self):
      try:
        pws = gdata.photos.service.PhotosService()
        limit = None
        if self.num_albums > 0: limit = self.num_albums
        self.__feed__ = \
            pws.GetUserFeed(user=str(self.email), limit=limit)
        # if you cache the feed, also cache user info
        self.__userinfo__ = UserInfo(self.__feed__.user.text,
                                     self.__feed__.nickname.text,
                                     self.__feed__.author[0].uri.text,
                                     self.__feed__.total_results.text,
                                     self.__feed__.updated.text,
                                     self.__feed__.id.text,
                                     self.__feed__.thumbnail.text)
        self.__updated__ = time.time()
      except gdata.photos.service.GooglePhotosException:
        self.__feed__ = None
    return self.__feed__

  # dynamic property
  feed = property(_cache_feed)

  def _sorted_feed(self):
    if not hasattr(self, '__sorted__') or not self.__sorted__ or outdated(self):
      self.__sorted__ = sorted([PicasaWebAlbum(k, self) for k in self.feed.entry])
    return self.__sorted__

  # dynamic property
  sorted = property(_sorted_feed)

  def _last_album(self):
    return self.sorted[-1]

  # dynamic property
  last = property(_last_album)

  def __unicode__(self):
    """A string representation of myself"""
    if self.num_albums:
      if self.num_albums == 1:
        return ugettext(u'Last uploaded album of %(email)s' % {'email': self.email})
      else:
        return ugettext(u'%(email)s, last %(num_albums)s albums' % \
            {'email': self.email, 'num_albums': self.num_albums})

    return ugettext(u'%(email)s' % {'email': self.email})

class CalendarEntry:
  """This class wraps a calendar entry and allows more efficient sorting"""

  def __init__(self, feed_entry, parent):
    self.start_date = gd_date(feed_entry.when[0].start_time)
    self.end_date = gd_date(feed_entry.when[0].end_time)
    self.where = feed_entry.where[0].value_string
    self.title = feed_entry.title.text
    self.description = feed_entry.content.text
    self.link = feed_entry.link[0].href
    self.parent = parent

  def ends_at_same_day(self):
    return self.start_date.date() == self.end_date.date()

  def __hash__(self):
    return hash(self.start_date)

  def __cmp__(self, other):
    return cmp(self.start_date, other.start_date)

class Calendar(models.Model):
  """This model describes a particular calendar in Google Calendar."""

  calendar_id = models.EmailField(_('Calendar identifier'), max_length=512,
      unique=True, help_text=_('Insert the identifier of a google calendar in the form of secret@domain. This identifier can be read by going into the calendar details of your google account.'))

  class Meta: 
    verbose_name = _(u'google calendar')
    verbose_name_plural = _(u'google calendars')

  def _cache_feed(self):
    if not hasattr(self, '__feed__') or not self.__feed__ or outdated(self):
      try:
        cal = gdata.calendar.service.CalendarService()
        start_date = time.strftime('%Y-%m-%d')
        self.__feed__ = cal.GetCalendarEventFeed(uri='http://www.google.com/calendar/feeds/%s/public/full?start-min=%s' % (self.calendar_id, start_date))
        self.__updated__ = time.time()
      except gdata.service.RequestError:
        self.__feed__ = None
    return self.__feed__

  # dynamic property
  feed = property(_cache_feed)

  def _sorted_feed(self):
    if not hasattr(self, '__sorted__') or not self.__sorted__ or outdated(self):
      if self.feed:
        self.__sorted__ = sorted([CalendarEntry(k, self) for k in self.feed.entry])
      else: self.__sorted__ = []
    return self.__sorted__

  # dynamic property
  sorted = property(_sorted_feed)

  def _next_event(self):
    return sorted[-1]

  # dynamic property
  next = property(_next_event)

  def _updated(self):
    return gd_date(self.feed.updated.text)

  # dynamic property
  updated = property(_updated)

  def __unicode__(self):
    """A string representation of myself"""
    return ugettext(u'Public google calendar "%s"' % self.calendar_id)

class YouTubeVideo:
  """This is a wrapper to make easier the manipulation of YouTube videos."""

  FlashPlayerTemplate = '<object width="425" height="355"><param name="movie" value="%(url)s"></param><param name="wmode" value="transparent"></param><embed src="%(url)s" type="application/x-shockwave-flash" wmode="transparent" width="425" height="355"></embed></object>'
  DefaultPlayerProperties = {
      'color1': '0xe1600f',
      'color2': '0xfebd01',
      }

  def __init__(self, service, entry, parent):
    """Initialize from Google data feed entry from YouTube."""
    video_link = get_video_link(entry.link, YOUTUBE_VIDEO_DATA)
    if not video_link:
      raise RuntimeError, 'Cannot find relevant video link in %s' % \
          [k.href for k in entry.link]
    self.youtube_link = get_video_link(entry.link, YOUTUBE_VIDEO_PAGE)
    self.playlist_entry = entry
    self.original_entry = service.GetYouTubeVideoEntry(video_link)
    self.author = entry.author[0].name.text
    self.description = entry.description.text
    if isinstance(self.description, str): 
      self.description = self.description.strip()
    self.url = entry.media.player.url
    self.duration = entry.media.duration.seconds
    self.keywords = entry.media.keywords.text
    self.title = entry.media.title.text
    self.thumbnail = entry.media.thumbnail[3]
    self.published = gd_date(self.original_entry.published.text)
    self.swfurl = self.original_entry.GetSwfUrl()
    self.parent = parent

  def flash_player_html(self, properties=None):
    """Returns the flash player embeddeable html. "properties" should be a
    dictionary of terms defined here: 
    http://code.google.com/apis/youtube/player_parameters.html"""
    if properties is None: properties = YouTubeVideo.DefaultPlayerProperties

    url = self.swfurl
    extras = '&'.join(['%s=%s' % (k,v) for (k,v) in properties.iteritems()])
    if extras: url = '&'.join([url, extras])
    return YouTubeVideo.FlashPlayerTemplate % {'url': url}

  def _id(self):
    return self.parent.sorted.index(self)

  # dynamic property
  id = property(_id)

  def __cmp__(self, other):
    return cmp(self.published, other.published)

class YouTubePlayList(models.Model):
  """This model describes a youtube play list."""

  name = models.CharField(_('Name'), max_length=256, help_text=_('Insert here a meaningful name so you remember what is this playlist key good for.'))
  list = models.CharField(_('YouTube playlist identifier'), max_length=64, unique=True, help_text=_('Insert the key of the youtube (public) playlist'))

  class Meta: 
    verbose_name = _(u'youtube playlist')
    verbose_name_plural = _(u'youtube playlists')

  def _cache_feed(self):
    if not hasattr(self, '__feed__') or not self.__feed__ or outdated(self):
      try:
        yts = gdata.youtube.service.YouTubeService()
        self.__feed__ = \
            yts.GetYouTubePlaylistVideoFeed(playlist_id=str(self.list))
        self.__updated__ = time.time()
      except Exception: 
        self.__feed__ = None
    return self.__feed__

  # dynamic property
  feed = property(_cache_feed)

  def _sorted_feed(self):
    if not hasattr(self, '__sorted__') or not self.__sorted__ or outdated(self):
      yts = gdata.youtube.service.YouTubeService()
      self.__sorted__ = sorted([YouTubeVideo(yts, k, self) for k in self.feed.entry])
    return self.__sorted__

  # dynamic property
  sorted = property(_sorted_feed)

  def _last_video(self):
    return self.sorted[-1]

  # dynamic property
  last = property(_last_video)

  def __unicode__(self):
    """A string representation of myself"""
    return ugettext(u'Youtube playlist "%(name)s"' % {'name': self.name})

