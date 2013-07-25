from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import Context, loader
from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.utils.timezone import utc, get_current_timezone
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import User, checkIn, companyLocation, Company, UserProfile, UserProfileManager
from .forms import MugForm
import datetime

# Stick into a view helper module
class ViewManager(object):
    
    @classmethod
    def login_handler(cls, request, **kwargs):
        if request.user.is_authenticated():
            return request.user
        else:
            send_to_login = reverse('onBaristaApp:login_view')
            redirect(send_to_login)
    
    @classmethod
    def view_manager(cls, request, view_name, companyID=0):
        user = ViewManager.login_handler(request)

        if user is None:
            raise PermissionDenied()

        else:
            userdetails = user.get_profile()

            # Make sure that the user has the rights to use the admin page
            if not userdetails.isCompanyAdmin and view_name == 'Admin':
                raise PermissionDenied()
            company= ''
            locations = ''
            companies = Company.objects.all()

            if companyID and companyID != '0':
                company = Company.objects.get(pk=companyID)
                locations = company.get_locations()

                for location in locations:
                    location.checkins = location.get_checkins()

            else:

                if userdetails.favCompany:
                    company = userdetails.favCompany
                    locations = company.get_locations()

                for location in locations:
                    location.checkins = location.get_checkins()

            # Create the default parameters that most views use
            manager_dict = {'navFlag':{'Home':'', 'Baristas':'', 'ManageFavs':'', 'ManageProfile':'', 'Admin':''},
             'companies':companies, 
             'locations':locations, 
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

def login_view(request):
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
                # Initialize variables, only populate them if the logic conditions allow it.
                favCompany= Company()
                favCompany.pk = '0'
                # Populate database table with UserProfile class attributes.  Store object as userdetails.
                userdetails = user.get_profile()

                if userdetails.favCompany:
                    favCompany = userdetails.favCompany
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
        userdetails = user.get_profile()

        if userdetails.favCompany:
            favCompany = userdetails.favCompany
            return companyHome(request, favCompany.pk)
        return companyHome(request, 0)

    else:
        # If no information has been submitted, and there is no active 'user' in session (login).
        return render(request, 'login.html')

def companyHome(request, companyID=0):
    manager_dict, user, userdetails = ViewManager.view_manager(request, 'Home', companyID)

    local_dict = {
                }
    params = dict(manager_dict.items() + local_dict.items())
    return render(request, 'home.html', params)

def checkInPost(request):
    user = ViewManager.login_handler(request)

    location = companyLocation.objects.get(pk=request.POST['location'])
    
    # Create new check in object with the barista ( logged in user ) and associate it with the location.
    # Creates and saves the checkIn object.
    # Deletes the old checkIn object if there is one, and creates a new one.
    checkIn.create(user, location)
    # Edit and save user details to reflect the checked-in status.
    # ModelManager.check_in_user(user, request)
    userdetails = user.get_profile()
    userdetails.objects.check_in_user(user, request)
    return HttpResponseRedirect(reverse('onBaristaApp:baristas', kwargs={'companyID':location.companyID.pk}))

def checkOutPost(request):
    user = ViewManager.login_handler(request)
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
    user = ViewManager.login_handler(request)
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
    manager_dict, user, userdetails = ViewManager.view_manager(request, 'Baristas', companyID)

    local_dict = {
               'message':message,
               }
    params = dict(manager_dict.items() + local_dict.items())
    return render(request, 'baristas.html', params)

def favorites(request, message='', navigation=False, fullSpanBlock=True):
    manager_dict, user, userdetails = ViewManager.view_manager(request, 'ManageFavs')

    manager_dict['message'] = message
    manager_dict['navigation'] = navigation
    manager_dict['fullSpanBlock'] = fullSpanBlock
    return render(request, 'favorites.html', manager_dict)


def update_favs(request):
    manager_dict, user, userdetails = ViewManager.view_manager(request, 'Baristas')

    userdetails.update_favs(request.POST['companyID'], request.POST['baristaID'])
    request.session['user'] = user
    manager_dict['navigation'] = False
    return favorites(request, "Your favorites have been updated", manager_dict)

def baristaList(request):
    user = ViewManager.login_handler(request)
    userdetails = user.get_profile()
    userdetailsList = UserProfile.objects.filter(userType='Barista', full_name__startswith = request.POST['searchString']).exclude(pk = userdetails.pk)
    return render(request, 'autocompleteList.html', {'results':userdetailsList})

def companyList(request):
    user = ViewManager.login_handler(request)
    companies = Company.objects.filter(companyName__startswith = request.POST['searchString'])
    return render(request, 'autocompleteList.html', {'results':companies})

def view_profile(request, fullSpanBlock=True):
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
    manager_dict['fullSpanBlock'] = fullSpanBlock
    manager_dict['form'] = form
    manager_dict['user'] = userdetails
    request.session['user'] = user
    return render(request, 'profile.html', manager_dict)

def admin_panel(request):
    manager_dict, user, userdetails = ViewManager.view_manager(request, 'Admin')
    return render(request, 'admin.html', manager_dict)

def logout_view(request):
    logout(request)

    if ('user' in request.session):
        del request.session['user']
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
