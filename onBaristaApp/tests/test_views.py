from django.utils import unittest
from django.test import TestCase
from django.http import QueryDict
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.utils.importlib import import_module
from django.utils.timezone import utc, get_current_timezone, activate, localtime
from django.test.client import Client, RequestFactory
from django.conf import settings
from onBaristaApp.models import User, checkIn, companyLocation, Company, UserProfile, UserProfileManager
from onBaristaApp.views import ViewManager, login_view, companyHome, checkInPost, checkOutPost, mark_as_barista, companyBaristas, favorites, update_favs, baristaList, companyList, view_profile, admin_panel, logout_view, register
import datetime

def create_company_and_associated_location(companyName, companyContact, street, city, state, zipCode):
    company = Company.objects.create(companyName=companyName, companyContact=companyContact)
    companyLocation.objects.create(companyID=company, street=street, city=city, state=state, zipCode=zipCode)

def create_barista_and_details(username, password, email, usercheckedin, first_name, last_name, mug):
    barista = User(username=username, password=password, email=email)
    # Not necessary for these tests, and significantly slows down test time
    # barista.set_password(password)
    # Proper hashed password is manually set for tests that need them
    barista.save()
    baristadetails = barista.get_profile()
    baristadetails.userType = 'Barista'
    baristadetails.usercheckedin = usercheckedin
    baristadetails.first_name = first_name
    baristadetails.last_name = last_name
    baristadetails.mug = mug
    baristadetails.save()

def create_user_and_details(username, password, email, first_name, last_name, mug, favCompany, favBaristaObj):
    user = User(username=username, password=password, email=email)
    # Not necessary for all tests, and significantly slows down test time
    # Find a good way to only use set_password for relevant tests
    # Or use a cheaper function
    user.set_password(password)
    user.save()
    userdetails = user.get_profile()
    userdetails.mug = mug
    userdetails.first_name = first_name
    userdetails.last_name = last_name
    userdetails.favCompany = favCompany
    userdetails.favBaristaObj = favBaristaObj
    userdetails.save()

def create_user_and_details_with_set_password(username, password, email, first_name, last_name, mug, favCompany, favBaristaObj):
    user = User(username=username, password=password, email=email)
    user.set_password(password)
    user.save()
    userdetails = user.get_profile()
    userdetails.mug = mug
    userdetails.first_name = first_name
    userdetails.last_name = last_name
    userdetails.favCompany = favCompany
    userdetails.favBaristaObj = favBaristaObj
    userdetails.save()

def create_checkin_and_association(barista, company, checkedin):
    checkin = checkIn()
    checkin.barista = User.objects.get(username=barista.username)
    checkin.location = companyLocation.objects.get(companyID=company)
    checkin.inTime = timezone.now()
    checkin.outTime = timezone.now()
    checkin.checkedin = checkedin
    checkin.save()

# def create_generic_test_user_with_hashed_password():
#     create_user_and_details_with_set_password(
#         username='generic_chris', 
#         password='bagel', 
#         email='generic_chrisvanschyndel@gmail.com', 
#         first_name='generic_chris', 
#         last_name='generic_van schyndel', 
#         mug='U1.jpg', 
#         favCompany=Company.objects.get(companyName="Voltage"), 
#         favBaristaObj=User.objects.get(username='jimmy').get_profile()
#         )
#     return User.objects.get(username='generic_chris')

class BroadViewTest(TestCase):

    def setUp(self):
        # http://code.djangoproject.com/ticket/10899
        settings.SESSION_ENGINE = 'django.contrib.sessions.backends.file'
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save()
        self.session = store
        self.client = Client()
        self.client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key
        self.factory = RequestFactory()
        create_company_and_associated_location(
            companyName="Voltage", 
            companyContact="Lucy", 
            street="275 3rd street", 
            city="Cambridge", 
            state="Massachusetts", 
            zipCode="21432"
            )
        self.company = Company.objects.get(companyName="Voltage")
        self.company_location = companyLocation.objects.get(zipCode="21432")
        create_barista_and_details(
            username='jimmy', 
            password='popcorn', 
            email='jimmydean@bagel.com', 
            usercheckedin=True, 
            first_name='jimmy', 
            last_name='dean', 
            mug='abra.jpg'
            )
        self.barista = User.objects.get(username='jimmy')
        self.baristadetails = self.barista.get_profile()
        create_user_and_details(
            username='chris', 
            password='bagel', 
            email='chrisvanschyndel@gmail.com', 
            first_name='chris', 
            last_name='van schyndel', 
            mug='U1.jpg', 
            favCompany=self.company, 
            favBaristaObj=self.baristadetails
            )
        self.user = User.objects.get(username='chris')
        self.userdetails = self.user.get_profile()
        create_checkin_and_association(barista=self.barista, company=self.company, checkedin=True)
        self.checkin = checkIn.objects.get(barista=self.barista)

    def test_that_login_view_get_with_no_user_returns_200(self):
        request = self.factory.get('/')
        request.session = self.session
        response = login_view(request)
        self.assertEquals(response.status_code, 200)

    def test_that_login_view_get_with_logged_in_user_returns_200(self):
        request = self.factory.get('/')
        request.session = self.session
        request.session['user'] = self.user
        request.user = self.user
        response = login_view(request)
        self.assertEquals(response.status_code, 200)

    def test_that_login_view_post_with_correct_credentials_returns_200(self):
        request = self.factory.post('/', {'username':'chris', 'password':'bagel'})
        request.session = self.session
        request.user = self.user
        response = login_view(request)
        self.assertEquals(response.status_code, 200)

    def test_that_login_view_post_with_correct_credentials_but_inactive_user_returns_200(self):
        # This is an unimplemented feature - emails validating users as is_active
        # Currently all users are active by default, but the logic still exists for
        # non active users in the login view
        request = self.factory.post('/', {'username':'chris', 'password':'bagel'})
        self.user.is_active = False
        self.user.save()
        request.session = self.session
        request.user = self.user
        response = login_view(request)
        self.assertEquals(response.status_code, 200)

    def test_that_login_view_post_with_invalid_user_credentials_returns_200(self):
        request = self.factory.post('/', {'username':'bad_username', 'password':'bad_password'})
        request.session = self.session
        response = login_view(request)
        self.assertEquals(response.status_code, 200)

    def test_that_logout_url_with_session_returns_200(self):
        request = self.factory.get('/logout/')
        request.session = self.session
        request.session['user'] = self.user
        request.user = self.user
        response = logout_view(request)
        self.assertEquals(response.status_code, 200)

    def test_that_logout_url_without_session_returns_200(self):
        request = self.factory.get('/logout/')
        request.session = self.session
        response = logout_view(request)
        self.assertEquals(response.status_code, 200)
        
    def test_that_checkIn_button_url_with_logged_in_user_that_is_not_a_barista_returns_PermissionDenied(self):
        request = self.factory.post('/checkIn/', {'location': 1})
        request.session = self.session
        request.session['user'] = self.user
        request.user = self.user
        # Find a more appropriate use of TestCase for this test.
        try:
            response = checkInPost(request)
            self.assertEquals('Invalid UserType Consumer', 'Accessed CheckIn Button')
        except (PermissionDenied):
            self.assertEquals('PermissionDenied', 'PermissionDenied')
        
    # def test_that_checkOut_url_returns_200(self):
    #     request = self.factory.get('/checkOut/')
    #     request.user = self.user
    #     self.assertEquals(response.status_code, 200)
        
    # def test_that_baristas_url_returns_200(self):
    #     request = self.factory.get('/baristas/')
    #     request.user = self.user
    #     self.assertEquals(response.status_code, 200)
        
    # def test_that_baristasCheck_url_returns_200(self):
    #     request = self.factory.get('/baristasCheck/')
    #     request.user = self.user
    #     self.assertEquals(response.status_code, 200)
        
    # def test_that_favorites_url_returns_200(self):
    #     request = self.factory.get('/favorites/')
    #     request.user = self.user
    #     self.assertEquals(response.status_code, 200)
        
    # def test_that_updateFavs_url_returns_200(self):
    #     request = self.factory.get('/updateFavs/')
    #     request.user = self.user
    #     self.assertEquals(response.status_code, 200)
        
    # def test_that_baristaList_url_returns_200(self):
    #     request = self.factory.get('/baristaList/')
    #     request.user = self.user
    #     self.assertEquals(response.status_code, 200)
        
    # def test_that_companyList_url_returns_200(self):
    #     request = self.factory.get('/companyList/')
    #     request.user = self.user
    #     self.assertEquals(response.status_code, 200)
        
    # def test_that_register_url_returns_200(self):
    #     request = self.factory.get('/register/')
    #     request.user = self.user
    #     self.assertEquals(response.status_code, 200)
        
    # def test_that_home_url_returns_200(self):
    #     request = self.factory.get('/home/')
    #     request.user = self.user
    #     self.assertEquals(response.status_code, 200)
        
    # def test_that_home_1_url_returns_200(self):
    #     request = self.factory.get('/home/1/')
    #     request.user = self.user
    #     self.assertEquals(response.status_code, 200)
        
    # def test_that_Profile_url_returns_200(self):
    #     request = self.factory.get('/Profile/')
    #     request.user = self.user
    #     self.assertEquals(response.status_code, 200)

    # def test_that_AdminPanel_url_returns_200(self):
    #     request = self.factory.get('/AdminPanel/')
    #     request.user = self.user
    #     self.assertEquals(response.status_code, 200)

        

# def get_all_urls():
#     return ['/',
#             '/logout/',
#             '/checkIn',
#             '/checkOut/',
#             '/baristas/',
#             '/baristasCheck/',
#             '/favorites/',
#             '/updateFavs/',
#             '/baristaList/',
#             '/companyList/',
#             '/register/',
#             # This view requires a company ID and will need to have a valid company, set to 1 here.
#             '/home/1/',
#             '/home/',
#             '/Profile/',
#             '/AdminPanel/'
#             ]