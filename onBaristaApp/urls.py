from django.conf.urls import patterns, url
from django.contrib.auth import authenticate
from onBaristaApp import views

urlpatterns = patterns('',
			url(r'^$', views.login_view, name='login_view'),
			url(r'^logout/$', views.logout_view, name='logout'),
			url(r'^checkIn/$', views.checkInPost, name='checkInPost'),
			url(r'^checkOut/$', views.checkOutPost, name='checkOutPost'),
			url(r'^baristas/(?P<companyID>\d+)/$', views.companyBaristas, name='baristas'),
			url(r'^baristas/$', views.login_view, name='bad_baristas'),
			url(r'^baristasCheck/$', views.mark_as_barista, name='mark_as_barista'),
			url(r'^favorites/$', views.favorites, name='favorites'),
			url(r'^updateFavs/$', views.update_favs, name='updateFavs'),
			url(r'^baristaList/$', views.baristaList, name='baristaList'),
			url(r'^companyList/$', views.companyList, name='companyList'),
			url(r'^register/$', views.register, name='register'),
			url(r'^home/(?P<companyID>\d+)/$', views.companyHome, name='companyHome'),
			url(r'^home/$', views.login_view, name='login_view'),
			url(r'^Profile/$', views.view_profile, name='view_profile'),
			url(r'^AdminPanel/$', views.admin_panel, name='admin_panel'),
			url(r'^set_timezone/$', views.set_timezone, name='set_timezone'),
			)