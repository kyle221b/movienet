from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView
from movieapp import views


urlpatterns = patterns('',
    # ex: /movieapp/add
    url(r'add$', views.add_movie, name='add_movie'),
    # ex: /movie/5/
    url(r'movie/(?P<movieid>\d+)/$', views.movie, name='movie'),
    # ex: /actor/5/
    url(r'actor/(?P<actorid>\d+)/$', views.actor, name='actor'),
    # ex: /director/5
    url(r'^director/(?P<did>\d+)/$', views.director, name='director'),
    url(r'^find/$', views.find),
    url(r'^find/advanced/$', views.advancedfind),
    url(r'^rate/(?P<movieid>\d+)$', views.rate, name='rate')
)
