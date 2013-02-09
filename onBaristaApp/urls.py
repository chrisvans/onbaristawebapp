from django.conf.urls import patterns, url
from onBaristaApp import views

urlpatterns = patterns('',
			url(r'^$', views.login, name = 'login'),
			)