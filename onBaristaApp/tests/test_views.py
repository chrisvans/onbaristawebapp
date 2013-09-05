from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import QueryDict
from django.test import TestCase
from django.test.client import Client, RequestFactory
from django.utils import unittest
from django.utils import timezone
from django.utils.importlib import import_module
from django.utils.timezone import utc, get_current_timezone, activate, localtime
from onBaristaApp.models import checkIn, companyLocation, Company, UserProfile, UserProfileManager
from onBaristaApp.views import ViewManager, login_view, companyHome, checkInPost, checkOutPost, mark_as_barista, companyBaristas, favorites, update_favs, baristaList, companyList, view_profile, admin_panel, logout_view, register
import datetime

def create_company_and_associated_location(companyName, companyContact, street, city, state, zipCode):
    company = Company.objects.create(companyName=companyName, companyContact=companyContact)
    companyLocation.objects.create(companyID=company, street=street, city=city, state=state, zipCode=zipCode)

def create_barista_and_details(username, password, email, usercheckedin, first_name, last_name, mug):
    barista = User(username=username, password=password, email=email)
    barista.set_password(password)
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
        self.anon_user = AnonymousUser()
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
        self.checkin = checkIn.objects.filter(is_active=True).get(barista=self.barista)
        create_barista_and_details(
            username='quayle', 
            password='theozman', 
            email='quayle@cleric.com', 
            usercheckedin=False, 
            first_name='quayle', 
            last_name='thecleric', 
            mug='alakazam.jpg'
            )
        self.barista2 = User.objects.get(username='quayle')
        self.barista2details = self.barista.get_profile()
        self.barista2details.employer_id = 1
        self.barista2details.save()

    def test_that_login_view_get_with_no_user_returns_200(self):
        request = self.factory.get('/')
        request.session = self.session
        request.user = self.anon_user
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

    def test_that_logout_url_with_session_user_returns_200(self):
        request = self.factory.get('/logout/')
        request.session = self.session
        request.session['user'] = self.user
        request.user = self.user
        response = logout_view(request)
        self.assertEquals(response.status_code, 200)

    def test_that_logout_url_without_session_user_returns_200(self):
        request = self.factory.get('/logout/')
        request.session = self.session
        response = logout_view(request)
        self.assertEquals(response.status_code, 200)
        
    def test_that_checkIn_button_url_with_logged_in_user_that_is_not_a_barista_returns_PermissionDenied(self):
        request = self.factory.post('/checkIn/', {'location': 1})
        request.session = self.session
        request.session['user'] = self.user
        request.user = self.user
        try:
            response = checkInPost(request)
            self.assertEquals('Invalid UserType Consumer', 'Accessed CheckIn Button')
        except (PermissionDenied):
            self.assertEquals('Permission was denied', 'Permission was denied')

    def test_that_checkIn_button_url_with_logged_in_user_that_is_a_barista_returns_302(self):
        request = self.factory.post('/checkIn/', {'location': 1})
        request.session = self.session
        request.session['user'] = self.barista
        request.user = self.barista
        response = checkInPost(request)
        self.assertEquals(response.status_code, 302)

    def test_that_checkIn_button_with_proper_user_redirects_to_baristas_view_with_200(self):
        self.client.login(username='jimmy', password='popcorn')
        response = self.client.post('/checkIn/', {'location': 1})
        self.assertRedirects(response, reverse('onBaristaApp:baristas', kwargs={'companyID':1}), status_code=302, target_status_code=200)

    def test_that_checkOut_button_url_with_logged_in_user_that_is_not_a_barista_returns_403(self):
        request = self.factory.post('/checkOut/', {'location': 1})
        request.session = self.session
        request.session['user'] = self.user
        request.user = self.user
        try:
            response = checkOutPost(request)
            self.assertEquals('Invalid UserType Consumer', 'Accessed CheckIn Button')
        except (PermissionDenied):
            self.assertEquals('Permission was denied', 'Permission was denied')

    def test_that_checkOut_button_url_with_logged_in_user_that_is_a_barista_returns_302(self):
        request = self.factory.post('/checkOut/', {'location': 1})
        request.session = self.session
        request.session['user'] = self.barista
        request.user = self.barista
        response = checkOutPost(request)
        self.assertEquals(response.status_code, 302)

    def test_that_checkOut_button_with_proper_user_redirects_to_baristas_view_with_200(self):
        self.client.login(username='jimmy', password='popcorn')
        response = self.client.post('/checkOut/', {'location': 1})
        self.assertRedirects(response, reverse('onBaristaApp:baristas', kwargs={'companyID':1}), status_code=302, target_status_code=200)
        
    def test_that_baristas_url_with_user_and_no_user_returns_200(self):
        response = self.client.get('/baristas/')
        self.assertEquals(response.status_code, 200)
        self.client.login(username='chris', password='bagel')
        response = self.client.get('/baristas/')
        self.assertEquals(response.status_code, 200)

    def test_that_baristas_url_with_companyID_with_user_returns_200(self):
        request = self.factory.get('/baristas/1')
        request.session = self.session
        request.session['user'] = self.user
        request.user = self.user
        response = companyBaristas(request)
        self.assertEquals(response.status_code, 200)

    def test_that_baristas_url_with_companyID_with_no_user_returns_403(self):
        request = self.factory.get('/baristas/1')
        request.session = self.session
        request.session['user'] = self.anon_user
        request.user = self.anon_user
        try:
            response = companyBaristas(request)
            self.assertEquals('Anonymous User', 'Accessed baristas/1 url')
        except (PermissionDenied):
            self.assertEquals('Permission was denied', 'Permission was denied')

    def test_that_baristasCheck_url_with_user_with_userType_Consumer_returns_200_and_changes_UserType_to_Barista(self):
        request = self.factory.get('/baritasCheck/')
        request.session = self.session
        request.session['user'] = self.user
        request.user = self.user
        response = mark_as_barista(request)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(request.session['user'].get_profile().userType, 'Barista')

    def test_that_baristasCheck_with_user_with_userType_Barista_returns_200(self):
        # This will occur if a user who just used the mark_as_barista button
        # resubmits the same page request
        request = self.factory.get('/baritasCheck/')
        request.session = self.session
        request.session['user'] = self.barista
        request.user = self.barista
        response = mark_as_barista(request)
        self.assertEquals(response.status_code, 200)

    def test_that_baristasCheck_with_anon_user_returns_403(self):
        request = self.factory.get('/baritasCheck/')
        request.session = self.session
        request.session['user'] = self.anon_user
        request.user = self.anon_user
        try:
            response = mark_as_barista(request)
            self.assertEquals('Anonymous User', 'Accessed mark_as_barista url')
        except (PermissionDenied):
            self.assertEquals('Permission was denied', 'Permission was denied')

    def test_that_favorites_url_with_user_returns_200(self):
        request = self.factory.get('/favorites/')
        request.session = self.session
        request.session['user'] = self.user
        request.user = self.user
        response = favorites(request)
        self.assertEquals(response.status_code, 200)

    def test_that_favorites_url_with_anon_user_returns_403(self):
        request = self.factory.get('/favorites/')
        request.session = self.session
        request.session['user'] = self.anon_user
        request.user = self.anon_user
        try:
            response = favorites(request)
            self.assertEquals('Anonymous User', 'Accessed mark_as_barista url')
        except (PermissionDenied):
            self.assertEquals('Permission was denied', 'Permission was denied')

    def test_that_update_favs_url_with_user_returns_200_and_updates_favs_properly(self):
        request = self.factory.post('/updateFavs/', {'companyID': 1, 'baristaID': self.barista.id})
        request.session = self.session
        request.session['user'] = self.barista
        request.user = self.barista
        response = update_favs(request)
        self.assertEquals(response.status_code, 200)
        userdetails = request.session['user'].get_profile()
        self.assertEquals(userdetails.favBaristaObj, self.baristadetails)
        self.assertEquals(userdetails.favCompany.id, 1)

    def test_that_update_favs_url_with_anon_user_returns_403(self):
        request = self.factory.post('/updateFavs/', {'companyID': 1, 'baristaID': self.barista.id})
        request.session = self.session
        request.session['user'] = self.anon_user
        request.user = self.anon_user
        try:
            response = update_favs(request)
            self.assertEquals('Anonymous User', 'Accessed mark_as_barista url')
        except (PermissionDenied):
            self.assertEquals('Permission was denied', 'Permission was denied')

    def test_that_baristaList_url_with_user_returns_200(self):
        request = self.factory.post('/baristaList/', {'searchString': 'j'})
        request.session = self.session
        request.session['user'] = self.user
        request.user = self.user
        response = baristaList(request)
        self.assertEquals(response.status_code, 200)

    def test_that_baristaList_url_with_anon_user_returns_403(self):
        request = self.factory.post('/baristaList/', {'searchString': 'j'})
        request.session = self.session
        request.session['user'] = self.anon_user
        request.user = self.anon_user
        try:
            response = baristaList(request)
            self.assertEquals('Anonymous User', 'Accessed mark_as_barista url')
        except (PermissionDenied):
            self.assertEquals('Permission was denied', 'Permission was denied')

    def test_that_companyList_url_with_user_returns_200(self):
        request = self.factory.post('/companyList/', {'searchString': 'v'})
        request.session = self.session
        request.session['user'] = self.user
        request.user = self.user
        response = companyList(request)
        self.assertEquals(response.status_code, 200)

    def test_that_companyList_url_with_anon_user_returns_403(self):
        request = self.factory.post('/companyList/', {'searchString': 'v'})
        request.session = self.session
        request.session['user'] = self.anon_user
        request.user = self.anon_user
        try:
            response = companyList(request)
            self.assertEquals('Anonymous User', 'Accessed mark_as_barista url')
        except (PermissionDenied):
            self.assertEquals('Permission was denied', 'Permission was denied')

    def test_that_view_profile_url_with_user_returns_200(self):
        request = self.factory.get('/Profile/')
        request.session = self.session
        request.session['user'] = self.user
        request.user = self.user
        response = view_profile(request)
        self.assertEquals(response.status_code, 200)

# Incomplete Test
    # def test_that_view_profile_url_with_user_invalid_post_returns_default_image_and_returns_200(self):
        # request = self.factory.post('/Profile/', {})
        # request.session = self.session
        # request.session['user'] = self.user
        # request.user = self.user
        # response = view_profile(request)
        # self.assertEquals(response.status_code, 200)

    def test_that_view_profile_url_with_anon_user_returns_403(self):
        request = self.factory.get('/Profile/')
        request.session = self.session
        request.session['user'] = self.anon_user
        request.user = self.anon_user
        try:
            response = view_profile(request)
            self.assertEquals('Anonymous User', 'Accessed mark_as_barista url')
        except (PermissionDenied):
            self.assertEquals('Permission was denied', 'Permission was denied')

    def test_that_improper_url_returns_404(self):
        response = self.client.get('/bagels_and_hot_dogs')
        self.assertEquals(response.status_code, 404)

    def test_that_improper_user_accessing_admin_returns_403(self):
        request = self.factory.get('/AdminPanel/')
        request.session = self.session
        request.session['user'] = self.user
        request.user = self.user
        try:
            response = admin_panel(request)
            self.assertEquals('Non-Admin User', 'Accessed Admin Panel')
        except (PermissionDenied):
            self.assertEquals('Permission was denied', 'Permission was denied')

    def test_that_barista_user_viewing_baristas_shows_correct_feed_order_and_returns_200(self):
        request = self.factory.get('/baristas/1')
        request.session = self.session
        request.session['user'] = self.barista2
        request.user = self.barista2
        response = companyBaristas(request)
        self.assertEquals(response.status_code, 200)
        
# Incomplete Test
    # def test_that_register_url_returns_200(self):
    #     request = self.factory.get('/register/')
    #     request.user = self.user
    #     self.assertEquals(response.status_code, 200)