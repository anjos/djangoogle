from django.conf.urls.defaults import *

urlpatterns = patterns('',
                       url(r'^photos/$', 'djangoogle.views.view_albums',
                         name='picasaweb-view'),
                       url(r'^photos/(?P<id>\d+)/$',
                         'djangoogle.views.view_albums',
                         name='picasaweb-user-view'),
                       url(r'^photos/(?P<id>\d+)/(?P<index>\d+)/$',
                         'djangoogle.views.view_album',
                         name='picasaweb-view-album'),
                       url(r'^videos/$', 'djangoogle.views.view_videos',
                         name='youtube-view'),
                       url(r'^videos/(?P<id>\d+)/$',
                         'djangoogle.views.view_videos',
                         name='youtube-list-view'),
                       url(r'^videos/(?P<id>\d+)/(?P<index>\d+)/$',
                         'djangoogle.views.view_video',
                         name='youtube-view-video'),
                       url(r'^calendar/$', 'djangoogle.views.view_calendar',
                         name='calendar-view'),
                      )

