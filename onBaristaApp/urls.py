from django.conf.urls import patterns, url
from onBaristaApp import views

urlpatterns = patterns('',
			url(r'^$', views.login, name = 'login'),
			url(r'^logout/$', views.logout, name = 'logout'),
			url(r'^checkIn/$', views.checkIn, name='checkIn'),
			url(r'^baristas/$', views.baristas, name = 'baristas')
			)