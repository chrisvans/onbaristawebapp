from django.conf.urls import patterns, url
from onBaristaApp import views
from django.contrib.auth import authenticate

urlpatterns = patterns('',
			url(r'^$', views.login_view, name = 'login_view'),
			url(r'^logout/$', views.logout_view, name = 'logout'),
			url(r'^checkIn/$', views.checkInPost, name='checkInPost'),
			url(r'^checkOut/$', views.checkOutPost, name='checkOutPost'),
			url(r'^baristas/$', views.baristas, name = 'baristas'),
			url(r'^baristasCheck/$', views.mark_as_barista, name='mark_as_barista'),
			url(r'^Favorites/$', views.favorites, name='favorites'),
			url(r'^updateFavs/$', views.update_favs, name='updateFavs'),
			url(r'^baristaList/$', views.baristaList, name='baristaList'),
			url(r'^companyList/$', views.companyList, name='companyList'),
			url(r'^register/$', views.register, name = 'register'),
			url(r'^home/(?P<companyID>\d+)/$', views.companyHome, name='companyHome')
			)