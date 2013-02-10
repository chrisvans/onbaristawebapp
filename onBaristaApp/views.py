# Create your views here.
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import Context, loader
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from onBaristaApp.models import User, checkIn, companyLocation
from django.utils import timezone


def login(request):
	if request.method == 'POST':

		username = request.POST['username']
		password = request.POST['password']
		try:
			user = User.objects.get(userName = username, password = password)

		except (KeyError,User.DoesNotExist):
			return render(request, 'login.html', {'error_message':"user name or password do not match our records.",})
		else:
			request.session['username'] = user.userName
			request.session['user'] = user
			favCompany = user.favCompany
			locList = favCompany.get_locations()
			for location in locList:
				location.checkins = location.get_checkins()
			return render(request, 'home.html', {'user_name':user.userName, 'user':user, 'locations':locList})
	elif 'username' in request.session:
		print "username in session is not empty?"
		user = request.session['user']
		favCompany = user.favCompany
		locList = favCompany.get_locations()
		for location in locList:
			location.checkins = location.get_checkins()
		return render(request, 'home.html', {'user_name':user.userName, 'user':user, 'locations':locList})
	else:
		print "in else"
		return render(request, 'login.html')

def home(request):
	return render(request, 'home.html')

def checkInPost(request):
	location = companyLocation.objects.get(pk=request.POST['location'])
	user = request.session['user']
	currTime = timezone.now()
	ci = checkIn()
	ci.barista = user
	ci.location= location
	ci.inTime = currTime
	ci.outTime = currTime
	ci.save()
	return HttpResponseRedirect(reverse('onBaristaApp:login'))

def baristas(request):
	user = request.session['user']
	favCompany = user.favCompany
	locList = favCompany.get_locations()
	return render(request, 'baristas.html', {'user':user, 'locations':locList})

def logout(request):
	print "logging out"
	del request.session['username']
	return render(request, 'login.html')