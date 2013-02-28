# Create your views here.
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import Context, loader
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from onBaristaApp.models import User, checkIn, companyLocation, Company, UserProfile
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout

def login_handler(request):
	try:
		user = request.session['user']
		return False
	except KeyError:
		return True

def view_manager(request):
	pass

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

def home(request):
	if login_handler(request):
		return render(request, 'login.html')
	user = request.session['user']
	return render(request, 'home.html')

def companyHome(request, companyID=0):
	if login_handler(request):
		return render(request, 'login.html')
	user = request.session['user']
	userdetails = user.get_profile()
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
	return render(request, 'home.html', {'user_name':user.username,
										 'user':userdetails, 
										 'companies':companies, 
										 'locations':locations, 
										 'selectedID': str(companyID), 
										 'navigation': navigation,
										 'isCheckedIn':userdetails.isFavBarCheckedIn(),
										 'checkIn':userdetails.get_favBarCheckIn(),
										 'fromHome':fromHome,
										 'navFlag':{'Home':'active', 'Baristas':'', 'ManageFavs':''}})

def checkInPost(request):
	if login_handler(request):
		return render(request, 'login.html')
	user = request.session['user']
	location = companyLocation.objects.get(pk=request.POST['location'])
	# Is it just me or do the available timezone methods seem a bit lacking?
	currTime = timezone.now()
	# A user may not be checked in or checked out.  This only applies if they are.
	try:
		d = checkIn.objects.get(barista = user)
		# If the checkIn object's checkin flag is false, then the user is checked out.
		# Delete the checked out entry.
		if not d.checkedin:
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
	return HttpResponseRedirect(reverse('onBaristaApp:baristas'))

def checkOutPost(request):
	if login_handler(request):
		return render(request, 'login.html')
	location = companyLocation.objects.get(pk=request.POST['location'])
	user = request.session['user']
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
	return HttpResponseRedirect(reverse('onBaristaApp:baristas'))

def mark_as_barista(request):
	if login_handler(request):
		return render(request, 'login.html')
	user = request.session['user']
	userdetails = user.get_profile()
	if userdetails.userType == "Barista":
		print 'Warning from mark_as_barista, user accessed barista signup button or refreshed page on submit when user was already a barista.'
		return baristas(request)
	else:
		userdetails.userType = "Barista"
		userdetails.save()
		user.save()
		request.session['user'] = User.objects.get(username = user.username)
		return baristas(request, "Now registered as a barista!")

def baristas(request, message ='', companyID=0):
	if login_handler(request):
		return render(request, 'login.html')
	user = request.session['user']
	locations= ''
	userdetails = user.get_profile()
	if userdetails.favCompany:
		favCompany = userdetails.favCompany
		locations = favCompany.get_locations()
	# Added in usercheck dictionary pass so it could be used to verify if a user
	# was checked in at any location.
	companies = Company.objects.all()
	navigation = True
	fromBaristas = True
	return render(request, 'baristas.html', {'user':userdetails, 
											 'locations':locations,
											 'message':message,
											 'usercheck':userdetails.usercheckedin,
											 'companies':companies,
											 'navigation':navigation,
											 'fromBaristas':fromBaristas,
											 'navFlag':{'Home':'', 'Baristas':'active', 'ManageFavs':''}})

def favorites(request, message=''):
	if login_handler(request):
		return render(request, 'login.html')
	user = request.session['user']
	userdetails = user.get_profile()
	return render(request, 'Favorites.html', {'user':userdetails,
											  'message':message,
											  'navFlag':{'Home':'', 'Baristas':'', 'ManageFavs':'active'}})


def update_favs(request):
	if login_handler(request):
		return render(request, 'login.html')
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
	navigation = False
	return favorites(request, "Your favorites have been updated", {'navigation':navigation})

def baristaList(request):
	if login_handler(request):
		return render(request, 'login.html')
	user = request.session['user']
	ud = user.get_profile()
	userdetailsList = UserProfile.objects.filter(userType='Barista', full_name__startswith = request.POST['searchString']).exclude(pk = ud.pk)
	return render(request, 'autocompleteList.html', {'results':userdetailsList})

def companyList(request):
	if login_handler(request):
		return render(request, 'login.html')
	user = request.session['user']
	companies = Company.objects.filter(companyName__startswith = request.POST['searchString'])
	return render(request, 'autocompleteList.html', {'results':companies})

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
