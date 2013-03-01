# Create your views here.
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import Context, loader
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from onBaristaApp.models import User, checkIn, companyLocation, Company, UserProfile
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import PermissionDenied



def login_handler(request):
	try:
		user = request.session['user']
		return user
	except KeyError:
		return None

def view_manager(request, view_name):
	user = login_handler(request)
	if user is None:
		raise PermissionDenied()
	else:
		userdetails = user.get_profile()
		d = {'navFlag':{'Home':'', 'Baristas':'', 'ManageFavs':'', 'ManageProfile':''},
		 'user_name':user.username,
		 'user':userdetails,
		 'userObj': user,
		 'isCheckedIn':userdetails.isFavBarCheckedIn(),
		 'checkIn':userdetails.get_favBarCheckIn(),
		 'usercheck':userdetails.usercheckedin, 
		 }
		d['navFlag'][view_name] = 'active'
	return d, user, userdetails

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
				favCompany= Company()
				favCompany.pk = '0'
				# Populate database table with UserProfile class attributes.  Store object as userdetails.
				userdetails = user.get_profile()
				if userdetails.favCompany:
					favCompany = userdetails.favCompany
					locList = favCompany.get_locations()
					for location in locList:
						location.checkins = location.get_checkins()
				# After successful login, return to home, populate dictionary.
				return companyHome(request, favCompany.pk)
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
			return companyHome(request, favCompany.pk)
		return companyHome(request, 0)
	else:
		# If no information has been submitted, and there is no active 'user' in session (login).
		return render(request, 'login.html')

def companyHome(request, companyID=0):
	d, user, userdetails = view_manager(request, 'Home')

	company= ''
	locations = ''
	companies = Company.objects.all()
	if companyID and companyID != '0':
		company = Company.objects.get(pk=companyID)
		locations = company.get_locations()
		for location in locations:
			location.checkins = location.get_checkins()
	# Issues: navFlag, companies, locations, selectedID
	navigation = True
	fromHome = True

	local_d = {'companies':companies, 
				'locations':locations, 
				'selectedID': str(companyID), 
				'navigation': navigation,
				'fromHome':fromHome,}
	params = dict(d.items() + local_d.items())

	return render(request, 'home.html', params)

def checkInPost(request):
	user = login_handler(request)
	if user is None:
		return render(request, 'login.html')
	location = companyLocation.objects.get(pk=request.POST['location'])
	# Is it just me or do the available timezone methods seem a bit lacking?
	currTime = timezone.now()
	# A user may not be checked in or checked out.  This only applies if they are.
	try:
		d = checkIn.objects.get(barista = user)
		# If there is already a checkin object, delete it to reduce errors.
		# Also takes care of a checked out object.
		# Delete the checked out entry.
		d.delete()
	except (KeyError,checkIn.DoesNotExist):
		1+1
	# Initialize checkIn object, set it's attributes appropriately to reflect
	# user object, location checked in at, and current time.
	ci = checkIn()
	ci.barista = user
	ci.location = location
	ci.inTime = currTime
	# Set user's usercheckedin flag to True, and then refresh the current session user.
	userdetails = user.get_profile()
	userdetails.usercheckedin = True
	user.save()
	userdetails.save()
	request.session['user'] = User.objects.get(username = user.username)
	ci.save()
	return HttpResponseRedirect(reverse('onBaristaApp:baristas', kwargs={'companyID':location.companyID.pk}))

def checkOutPost(request):
	user = login_handler(request)
	if user is None:
		return render(request, 'login.html')
	location = companyLocation.objects.get(pk=request.POST['location'])
	currTime = timezone.now()
	# Same as checkInPost but inverted when necessary.
	d = checkIn.objects.get(barista = user)
	co = checkIn.objects.get(barista = user)
	if d.checkedin:
		d.delete()
	co.outTime = currTime
	co.checkedin = False
	userdetails = user.get_profile()
	userdetails.usercheckedin = False
	user.save()
	userdetails.save()
	request.session['user'] = User.objects.get(username = user.username)
	co.save()
	return HttpResponseRedirect(reverse('onBaristaApp:baristas', kwargs={'companyID':location.companyID.pk}))

def mark_as_barista(request):
	user = login_handler(request)
	if user is None:
		return render(request, 'login.html')
	userdetails = user.get_profile()
	if userdetails.userType == "Barista":
		print 'Warning from mark_as_barista, user accessed barista signup button or refreshed page on submit when user was already a barista.'
		return companyBaristas(request)
	else:
		userdetails.userType = "Barista"
		userdetails.save()
		user.save()
		request.session['user'] = User.objects.get(username = user.username)
		return companyBaristas(request, "Now registered as a barista!")

def companyBaristas(request, message='', companyID=0):
	d, user, userdetails = view_manager(request, 'Baristas')

	locations= ''
	if userdetails.favCompany:
		favCompany = userdetails.favCompany
		locations = favCompany.get_locations()
	if companyID and companyID != '0':
		company = Company.objects.get(pk=companyID)
		locations = company.get_locations()
		for location in locations:
			location.checkins = location.get_checkins()
	companies = Company.objects.all()
	navigation = True
	fromBaristas = True

	local_d = {'companyID':companyID,
			   'locations':locations,
			   'message':message,
			   'companies':companies,
			   'navigation':navigation,
			   'fromBaristas':fromBaristas,}
	params = dict(d.items() + local_d.items())

	return render(request, 'baristas.html', params)

def favorites(request, message='', navigation=False):
	params, user, userdetails = view_manager(request, 'ManageFavs')
	params['message'] = message
	params['navigation'] = navigation

	return render(request, 'Favorites.html', params)


def update_favs(request):
	params, user, userdetails = view_manager(request, 'Baristas')

	userdetails.update_favs(request.POST['companyID'], request.POST['baristaID'])

	request.session['user'] = user
	params['navigation'] = False

	return favorites(request, "Your favorites have been updated", params)

def baristaList(request):
	user = login_handler(request)
	if user is None:
		return render(request, 'login.html')
	ud = user.get_profile()
	userdetailsList = UserProfile.objects.filter(userType='Barista', full_name__startswith = request.POST['searchString']).exclude(pk = ud.pk)
	return render(request, 'autocompleteList.html', {'results':userdetailsList})

def companyList(request):
	user = login_handler(request)
	if user is None:
		return render(request, 'login.html')
	companies = Company.objects.filter(companyName__startswith = request.POST['searchString'])
	return render(request, 'autocompleteList.html', {'results':companies})

def view_profile(request):
	params, user, userdetails = view_manager(request, 'ManageProfile')
	return render(request, 'profile.html', params)

def logout_view(request):
	logout(request)
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
			user.full_name = first_name + " " + last_name
			user.save()
			user = authenticate(username=username, password=password)
			login(request, user)

			return render(request, 'login.html', {'success_message':"You successfully registered!  Now log in!",})
		else:
			return render(request, 'register.html', {'error_message':"Username already exists!",})
	else:
		return render(request, 'register.html')
