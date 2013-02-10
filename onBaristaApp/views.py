# Create your views here.
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import Context, loader
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from onBaristaApp.models import User, checkIn, companyLocation, Company
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
			locList=''
			if user.favCompany:
				favCompany = user.favCompany
				locList = favCompany.get_locations()
				for location in locList:
					location.checkins = location.get_checkins()
			return render(request, 'home.html', {'user_name':user.userName, 'user':user, 'locations':locList})
	elif 'username' in request.session:
		print "username in session is not empty?"
		user = request.session['user']
		locList=''
		if user.favCompany:
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

def mark_as_barista(request):
	print "in mark as barista"
	user = request.session['user']
	user.userType = "Barista"
	user.save()
	return baristas(request, "thanks for being barista!")
	#return HttpResponseRedirect(reverse('onBaristaApp:baristas', {'message':"thanks for being barista!",}))

def baristas(request, message =''):
	user = request.session['user']
	locList= ''
	if user.favCompany:
		favCompany = user.favCompany
		locList = favCompany.get_locations()
	return render(request, 'baristas.html', {'user':user, 'locations':locList, 'message':message})

def favorites(request, message=''):
	return render(request, 'Favorites.html', {'user':request.session['user'], 'message':message})


def update_favs(request):
	user = request.session['user']
	if request.POST['baristaID']:
		barista = User.objects.get(pk=request.POST['baristaID'])
		user.favBaristaObj = barista
	if request.POST['companyID']:
		company = Company.objects.get(pk=request.POST['companyID'])
		user.favCompany = company
	user.save()
	request.session['user'] = user
	return favorites(request, "Your favorites have been updated")

def baristaList(request):
	print request.POST['searchString']
	baristas = User.objects.filter(userType='Barista', firstName__startswith=request.POST['searchString'])
	return render(request, 'baristaList.html', {'baristas':baristas})

def companyList(request):
	companies = Company.objects.filter(companyName__startswith = request.POST['searchString'])
	return render(request, 'companyList.html', {'companies':companies})

def logout(request):
	if ('username' in request.session):
		del request.session['username']
	if ('user' in request.session):
		del request.session['user']
	return render(request, 'login.html')