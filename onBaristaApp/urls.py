from django.conf.urls import patterns, url
from onBaristaApp import views

urlpatterns = patterns('',
			url(r'^$', views.login, name = 'login'),
			url(r'^logout/$', views.logout, name = 'logout'),
			url(r'^checkIn/$', views.checkInPost, name='checkInPost'),
			url(r'^baristas/$', views.baristas, name = 'baristas'),
			url(r'^baristasCheck/$', views.mark_as_barista, name='mark_as_barista'),
			url(r'^Favorites/$', views.favorites, name='favorites'),
			url(r'^updateFavs/$', views.update_favs, name='updateFavs'),
			url(r'^baristaList/$', views.baristaList, name='baristaList')
			)