from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template import Context, loader
from django.utils.timezone import utc, get_current_timezone
from django.utils import timezone
from .models import checkIn, companyLocation, Company, UserProfile, UserProfileManager
from .forms import MugForm
import datetime
import pytz

# Stick into a view helper module
class ViewManager(object):
    
    @classmethod
    def login_handler(cls, request, **kwargs):
        if request.user.is_authenticated():
            return request.user
        else:
            raise PermissionDenied()
    
    @classmethod
    def view_manager(cls, request, view_name, companyID='0'):
        user = ViewManager.login_handler(request)

        userdetails = user.get_profile()
        # Make sure that the user has the rights to use the admin page
        if not userdetails.isCompanyAdmin and view_name == 'Admin':
            raise PermissionDenied()

        # This determines how the company feed data is represented in each view.
        if view_name == 'Baristas' and userdetails.usercheckedin:
            # If the current user is checked in, and viewing the barista check in page,
            # only show the company that they can check out from.
            companies = Company.objects.filter(id=checkIn.objects.filter(is_active=True).get(barista=user).location.companyID.pk)

        elif view_name == 'Baristas' and userdetails.employer_id != 0:
            # Brings the most recent checkin company to the top of the feed.
            # employer_id is set when a barista checks in at a company.
            # This list conversion from queryset may be too expensive, find a more effecient way to do this.
            companies = list(Company.objects.all())
            companies.insert(0, companies.pop(companies.index(Company.objects.get(id=userdetails.employer_id))))
        
        elif companyID != '0':
            # Brings the favorite barista's current checkin company to the top of the feed.
            # Company is only not '0' when the favorite barista navbar link is clicked.
            companies = list(Company.objects.all())
            companies.insert(0, companies.pop(companies.index(Company.objects.get(id=companyID))))
        
        elif userdetails.favCompany:
            # Brings the favorite company to the top of the feed.
            companies = list(Company.objects.all())
            companies.insert(0, companies.pop(companies.index(userdetails.favCompany)))
        
        else:
            # Display all companies.  This will need to change to be more dynamic when there are 
            # more than 20 companies.  Implement a search bar at this point.
            companies = Company.objects.all()

        # Create the default parameters that most views use
        manager_dict = {
         'navFlag':{'Home':'', 'Baristas':'', 'ManageFavs':'', 'ManageProfile':'', 'Admin':''},
         'companies':companies, 
         'selectedID': str(companyID), 
         'companyID':companyID,
         'user_name':user.username,
         'user':userdetails,
         'isCheckedIn':userdetails.isFavBarCheckedIn(),
         'checkIn':userdetails.get_favBarCheckIn(),
         'usercheck':userdetails.usercheckedin, 
             }

        # Set the 'active' class to the correct view
        manager_dict['navFlag'][view_name] = 'active'
        return manager_dict, user, userdetails

    @classmethod
    def is_barista(cls, user):
        userdetails = user.get_profile()
        if userdetails.userType == 'Barista':
            pass
        else:
            raise PermissionDenied()

def login_view(request):
    if request.method == 'POST':
        # Django's user authentication via user submission into form
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        # authenticate() returns None if the passed arguments are incorrect,
        # otherwise it returns the proper user object associated with them.

        if user is not None:

            if user.is_active:
                login(request, user)
                request.session['user'] = user
                userdetails = user.get_profile()
                request.session['django_timezone'] = pytz.timezone(userdetails.timezone)
                # Prioritize favorite company in index list of companies
                return companyHome(request, userdetails.get_favorite_company_id())

            else:
                # If user.is_active returns False.  Boolean that can be set manually.
                return render(request, 'login.html', {'error_message':"Your account has been disabled!",})
        
        else:
            # If authentication() returns None (fails).
            return render(request, 'login.html', {'error_message':"Username or password do not match our records.",})
            
    elif 'user' in request.session:
        # Do not show login view if user is already logged in, direct to homepage.
        user = request.session['user']
        userdetails = user.get_profile()
        return companyHome(request, userdetails.get_favorite_company_id())

    else:
        # If no information has been submitted, and there is no active 'user' in session (login).
        return render(request, 'login.html')

def companyHome(request, companyID='0'):
    # Homepage view.
    # The company ID being passed here is the user's favorite company,
    # populate this to the top of the feed.
    manager_dict, user, userdetails = ViewManager.view_manager(request, 'Home', companyID)

    local_dict = {
                }
    params = dict(manager_dict.items() + local_dict.items())
    return render(request, 'home.html', params)

def checkInPost(request):
    # Barista view - Check In Button.
    user = ViewManager.login_handler(request)
    # Verify that post is being sent by a user that is a barista
    ViewManager.is_barista(user)
    location = companyLocation.objects.get(pk=request.POST['location'])
    # Create new check in object with the barista ( logged in user ) and associate it with the location.
    # Deletes the old checkIn object if there is one, and creates a new one, saving it.
    checkIn.create(user, location)
    # Edit and save user details to reflect the checked-in status.
    companyID = location.companyID.pk
    UserProfile.objects.check_in_user(user, request, companyID)
    return HttpResponseRedirect(reverse('onBaristaApp:baristas', kwargs={'companyID':location.companyID.pk}))

def checkOutPost(request):
    # Barista view - Check Out Button.
    user = ViewManager.login_handler(request)
    # Verify that post is being sent by a user that is a barista
    ViewManager.is_barista(user)
    location = companyLocation.objects.get(pk=request.POST['location'])
    # Change check in object to reflect checked out status.
    check_in = checkIn.objects.filter(is_active=True).get(barista = user)
    check_in.check_out_user()
    UserProfile.objects.check_out_user(user, request)
    return HttpResponseRedirect(reverse('onBaristaApp:baristas', kwargs={'companyID':location.companyID.pk}))

def mark_as_barista(request):
    # Barista view - Register as Barista Button.
    user = ViewManager.login_handler(request)
    userdetails = user.get_profile()
    userdetails.userType = "Barista"
    userdetails.save()
    user.save()
    request.session['user'] = User.objects.get(username = user.username)
    return companyBaristas(request, "Now registered as a barista!")

def companyBaristas(request, message='', companyID='0'):
    # Barista view.
    manager_dict, user, userdetails = ViewManager.view_manager(request, 'Baristas', companyID)

    local_dict = {
               'message':message,
               }
    params = dict(manager_dict.items() + local_dict.items())
    return render(request, 'baristas.html', params)

def favorites(request, message='', navigation=False):
    # Manage Favorites page.
    manager_dict, user, userdetails = ViewManager.view_manager(request, 'ManageFavs')

    manager_dict['message'] = message
    manager_dict['navigation'] = navigation
    return render(request, 'favorites.html', manager_dict)


def update_favs(request):
    # Submit from Favorites page.
    manager_dict, user, userdetails = ViewManager.view_manager(request, 'Baristas')

    userdetails.update_favs(request.POST['companyID'], request.POST['baristaID'])
    request.session['user'] = user
    manager_dict['navigation'] = False
    return favorites(request, "Your favorites have been updated", manager_dict)

def baristaList(request):
    # Search form from Favorites page.
    user = ViewManager.login_handler(request)
    userdetails = user.get_profile()
    userdetailsList = UserProfile.objects.filter(userType='Barista', full_name__startswith = request.POST['searchString']).exclude(pk = userdetails.pk)
    return render(request, 'autocompleteList.html', {'results':userdetailsList})

def companyList(request):
    # Search form from Favorites page.
    user = ViewManager.login_handler(request)
    companies = Company.objects.filter(companyName__startswith = request.POST['searchString'])
    return render(request, 'autocompleteList.html', {'results':companies})

def view_profile(request):
    manager_dict, user, userdetails = ViewManager.view_manager(request, 'ManageProfile')

    if request.method == 'POST':
        form = MugForm(request.POST, request.FILES)

        if form.is_valid():
            userdetails.mug = request.FILES['mug']
            userdetails.save()
            request.session['user'] = user
            return HttpResponseRedirect(reverse('onBaristaApp:view_profile'))

    else:
        form = MugForm()
    manager_dict['form'] = form
    manager_dict['user'] = userdetails
    manager_dict['timezones'] = pytz.common_timezones
        # return render(request, 'profile.html', {'timezones': pytz.common_timezones})
    request.session['user'] = user
    return render(request, 'profile.html', manager_dict)

def admin_panel(request):
    manager_dict, user, userdetails = ViewManager.view_manager(request, 'Admin')
    return render(request, 'admin.html', manager_dict)

def logout_view(request):
    logout(request)
    return render(request, 'login.html')

def register(request):
    # Use a form - pass in dictionary of data
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']

        if username.strip() == '' or password.strip() == '' or email.strip() == '':
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
            return render(request, 'login.html', {'success_message':"You successfully registered!",})

        else:
            return render(request, 'register.html', {'error_message':"Username already exists!",})

    else:
        return render(request, 'register.html')


def set_timezone(request):
    user = ViewManager.login_handler(request)

    if request.method == 'POST':
        new_timezone = pytz.timezone(request.POST['timezone'])
        request.session['django_timezone'] = new_timezone
        userdetails = user.get_profile()
        userdetails.timezone = new_timezone
        userdetails.save()
        return redirect('/Profile/')

    else:
        return render(request, 'login.html')