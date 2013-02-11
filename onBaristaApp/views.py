# Create your views here.
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import Context, loader
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from onBaristaApp.models import User, UserManager, checkIn, companyLocation, Company
from django.utils import timezone
from django.contrib.auth import authenticate
# from onBaristaApp.models import UserProfile


def login_view(request):
	if request.method == 'POST':

		#username = request.POST['username']
		#password = request.POST['password']
		user = authenticate(username=request.POST['username'], password=request.POST['password'])
		if user is not None:
			if user.is_active:
				login(request, user)
				locList=''
				isFavBarCheckedIn = False
				checkInObj = ''
				if user.favCompany:
					favCompany = user.favCompany
					locList = favCompany.get_locations()
					for location in locList:
						location.checkins = location.get_checkins()
				if user.favBaristaObj:
					favBarista =user.favBaristaObj
					checkInObj = checkIn.objects.filter(barista = favBarista)
					if checkInObj:
						isFavBarCheckedIn = True
				return render(request, 'home.html', {'user_name':user.username, 'user':user, 'locations':locList,'checkIn':checkInObj, 'isCheckedIn': isFavBarCheckedIn})
			else:
				return render(request, 'login.html', {'error_message':"Your account has been disabled!",})
		else:
			return render(request, 'login.html', {'error_message':"Username or password do not match our records.",})
		#try:
		#	user = User.objects.get(username = username, password = password)

		#except (KeyError,User.DoesNotExist):
		#else:	
			#request.session['username'] = user.username
			#request.session['user'] = user
			
	elif 'username' in request.session:
		print "username in session is not empty?"
		user = request.session['user']
		locList=''
		if user.favCompany:
			favCompany = user.favCompany
			locList = favCompany.get_locations()
			for location in locList:
				location.checkins = location.get_checkins()
		return render(request, 'home.html', {'user_name':user.username, 'user':user, 'locations':locList})
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
	return HttpResponseRedirect(reverse('onBaristaApp:login_view'))

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
	baristas = User.objects.filter(userType='Barista', first_name__startswith=request.POST['searchString'])
	return render(request, 'baristaList.html', {'baristas':baristas})

def companyList(request):
	companies = Company.objects.filter(companyName__startswith = request.POST['searchString'])
	return render(request, 'companyList.html', {'companies':companies})

def logout_view(request):
	logout(request)
	#if ('username' in request.session):
	#	del request.session['username']
	#if ('user' in request.session):
	#	del request.session['user']
	return render(request, 'login.html')

def register(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		email = request.POST['email']
		first_name = request.POST['first_name']
		last_name = request.POST['last_name']
		barista_location = request.POST['barista_location']
		# UserProfile pass incomplete, excess information unused at this point.
		if username == '' or password == '' or email == '':
			return render(request, 'register.html', {'error_message':"A required field has been left empty!",})
		try:
			user = User.objects.get(username = username)

		except (KeyError,User.DoesNotExist):
			# Add in e-mail authentication!
			newuser = User.objects.create_user(username, email, password)
			newuser.first_name = first_name
			newuser.last_name = last_name
			newuser.save()
			authenticate(username, password)
			login(request, newuser)

			return render(request, 'register.html', {'success_message':"You successfully registered!",})
		else:
			return render(request, 'register.html', {'error_message':"Username already exists!",})
	else:
		return render(request, 'register.html')
