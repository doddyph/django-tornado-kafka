from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
    url(r'^register/$', views.register),
    # url(r'^login/$', views.user_login),
    url(r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout'),
)