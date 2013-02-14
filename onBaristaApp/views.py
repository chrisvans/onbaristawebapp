# Create your views here.
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import Context, loader
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from onBaristaApp.models import User, checkIn, companyLocation, Company
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from onBaristaApp.models import UserProfile


def login_view(request):
	# If you're at the login page and have submitted information, then..
	if request.method == 'POST':
		# Django's user authentication via user submission into form
		user = authenticate(username=request.POST['username'], password=request.POST['password'])
		# authenticate() returns None if the passed arguments are incorrect,
		# otherwise it returns the proper user object associated with them.
		if user is not None:
			if user.is_active:
				# Login passing in the user object gained from authenticate()
				login(request, user)
				# Pass the user into the session dictionary so we can keep track of the logged in user.
				# When the session dictionary is indexed with keyword 'user', returns this user object.
				request.session['user'] = user
				# Initialize variables, only populate them if the if conditions allow it.
				locList=''
				isFavBarCheckedIn = False
				checkInObj = ''
				# Populate database table with UserProfile class attributes.  Store object as userdetails.
				userdetails = user.get_profile()
				if userdetails.favCompany:
					favCompany = userdetails.favCompany
					locList = favCompany.get_locations()
					for location in locList:
						location.checkins = location.get_checkins()
				if userdetails.favBaristaObj:
					favBarista = userdetails.favBaristaObj
					checkInObj = checkIn.objects.filter(barista = favBarista)
					if checkInObj:
						isFavBarCheckedIn = True
				# After successful login, return to home, populate dictionary.
				return render(request, 'home.html', {'user_name':user.username, 'user':userdetails, 'locations':locList,'checkIn':checkInObj, 'isCheckedIn': isFavBarCheckedIn})
			else:
				# If user.is_active returns False.  Boolean that can be set manually.
				return render(request, 'login.html', {'error_message':"Your account has been disabled!",})
		else:
			# If authentication() returns None (fails).
			return render(request, 'login.html', {'error_message':"Username or password do not match our records.",})
			
	elif 'user' in request.session:
		# If the session dictionary has a 'user' keyword, the only means by which this happens is a successful login.
		# Update appropriate fields and sends user to the homepage instead of login.
		user = request.session['user']
		locList=''
		userdetails = user.get_profile()
		if userdetails.favCompany:
			favCompany = userdetails.favCompany
			locList = favCompany.get_locations()
			for location in locList:
				location.checkins = location.get_checkins()
		return render(request, 'home.html', {'user_name':user.username, 'user':userdetails, 'locations':locList})
	else:
		# If no information has been submitted, and there is no active 'user' in session (login).
		return render(request, 'login.html')

def home(request):
	return render(request, 'home.html')

def checkInPost(request):
	print request.POST['location']
	location = companyLocation.objects.get(pk=request.POST['location'])
	user = request.session['user']
	currTime = timezone.now()
	ci = checkIn()
	ci.barista = user
	ci.location= location
	ci.inTime = currTime
	#ci.outTime = currTime
	ci.save()
	return HttpResponseRedirect(reverse('onBaristaApp:login_view'))

#def checkOutPost(request):
#	location = companyLocation.objects.get(pk=request.POST['location'])
#	user = request.session['user']
#	currTime = timezone.now()
#	co = checkOut()
#	co.barista = user
#	co.location = location
#	co.outTime = currTime
#	co.save()
#	location.checkout(user)
#	return HttpResponseRedirect(reverse('onBaristaApp:login_view'))

def mark_as_barista(request):
	user = request.session['user']
	userdetails = user.get_profile()
	if userdetails.userType == "Barista":
		return baristas(request, "You're already a barista!")
	else:
		userdetails.userType = "Barista"
		userdetails.save()
		user.save()
		return baristas(request, "Now registered as a barista!")
	#return HttpResponseRedirect(reverse('onBaristaApp:baristas', {'message':"thanks for being barista!",}))

def baristas(request, message =''):
	user = request.session['user']
	locList= ''
	userdetails = user.get_profile()
	if userdetails.favCompany:
		favCompany = userdetails.favCompany
		locList = favCompany.get_locations()
	return render(request, 'baristas.html', {'user':userdetails, 'locations':locList, 'message':message})

def favorites(request, message=''):
	user = request.session['user']
	userdetails = user.get_profile()
	return render(request, 'Favorites.html', {'user':userdetails, 'message':message})


def update_favs(request):
	user = request.session['user']
	userdetails = user.get_profile()
	if request.POST['baristaID']:
		barista = UserProfile.objects.get(pk=request.POST['baristaID'])
		userdetails.favBaristaObj = barista
	if request.POST['companyID']:
		company = Company.objects.get(pk=request.POST['companyID'])
		userdetails.favCompany = company
	userdetails.save()
	request.session['user'] = user
	return favorites(request, "Your favorites have been updated")

def baristaList(request):
	userdetailsList = UserProfile.objects.filter(userType='Barista', user__first_name__startswith = request.POST['searchString'])
	return render(request, 'autocompleteList.html', {'results':userdetailsList})

def companyList(request):
	companies = Company.objects.filter(companyName__startswith = request.POST['searchString'])
	return render(request, 'autocompleteList.html', {'results':companies})

def logout_view(request):
	logout(request)
	#if ('username' in request.session):
	#	del request.session['username']
	if ('user' in request.session):
		del request.session['user']
	return render(request, 'login.html')

def register(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		email = request.POST['email']
		first_name = request.POST['first_name']
		last_name = request.POST['last_name']
		if username == '' or password == '' or email == '':
			return render(request, 'register.html', {'error_message':"A required field has been left empty!",})
		try:
			user = User.objects.get(username = username)

		except (KeyError,User.DoesNotExist):
			# Add in e-mail authentication!
			user = User.objects.create_user(username, email, password)
			user.first_name = first_name
			user.last_name = last_name
			user.save()
			user = authenticate(username=username, password=password)
			login(request, user)

			return render(request, 'login.html', {'success_message':"You successfully registered!  Now log in!",})
		else:
			return render(request, 'register.html', {'error_message':"Username already exists!",})
	else:
		return render(request, 'register.html')
