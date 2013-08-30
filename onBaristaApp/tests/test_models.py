from django.utils import unittest
from django.test import TestCase
from django.utils import timezone
from django.utils.timezone import utc, get_current_timezone, activate, localtime
from django.test.client import Client, RequestFactory
from onBaristaApp.models import User, checkIn, companyLocation, Company, UserProfile, UserProfileManager
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
    # Not necessary for these tests, and significantly slows down test time
    # user.set_password(password)
    # Proper hashed password is manually set for tests that need them
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

class CompanyTest(TestCase):

    def setUp(self):
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

    def test_unicode(self):
        self.assertEquals(type(u'a'), type(self.company.__unicode__()))
      
    def test_get_locations_returns_query(self):
        queryset = self.company.get_locations()
        self.assertEquals(type(Company.objects.all()), type(queryset))

    def test_get_locations_query_has_companyLocation_object(self):
        queryset = self.company.get_locations()
        for location in queryset:
            self.assertEquals(type(self.company_location), type(location))


class CompanyLocationTest(TestCase):

    def setUp(self):
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
        create_checkin_and_association(barista=self.barista, company=self.company, checkedin=True)
        create_barista_and_details(
            username='quayle', 
            password='popcorn', 
            email='leanqueen@bagel.com', 
            usercheckedin=False, 
            first_name='quayle', 
            last_name='the brave', 
            mug='whileawayflowers.jpg'
            )
        self.barista2 = User.objects.get(username='quayle')
        self.barista2details = self.barista2.get_profile()
        create_checkin_and_association(barista=self.barista2, company=self.company, checkedin=False)

    def test_unicode(self):
        self.assertEquals(type(u'a'), type(self.company_location.__unicode__()))

    def test_address_string_returns_unicode(self):
        self.assertEquals(type(u'a'), type(self.company_location.address_string()))

    def test_get_checkins_returns_query(self):
        self.assertEquals(type(Company.objects.all()), type(self.company_location.get_checkins()))

    def test_get_checkins_query_has_checkIn_object(self):
        checkinsquery = self.company_location.get_checkins()
        for checkin in checkinsquery:
            self.assertEquals(type(checkIn()), type(checkin))

    def test_get_checkin_out_returns_list(self):
        barista_list = self.company_location.get_checkin_out()
        self.assertEquals(type(barista_list), type([]))

    def test_get_checkin_out_list_has_baristas(self):
        barista_list = self.company_location.get_checkin_out()
        for barista in barista_list:
            baristadetails = barista.get_profile()
            self.assertEquals(baristadetails.userType, 'Barista')

    def test_get_checkin_out_barista_is_checked_out(self):
        barista_list = self.company_location.get_checkin_out()
        for barista in barista_list:
            baristadetails = barista.get_profile()
            self.assertEquals(False, baristadetails.usercheckedin)

    def test_get_checkin_in_returns_list(self):
        barista_list = self.company_location.get_checkin_in()
        self.assertEquals(type(barista_list), type([]))

    def test_get_checkin_in_list_has_baristas(self):
        barista_list = self.company_location.get_checkin_out()
        for barista in barista_list:
            self.assertEquals(self.baristadetails.userType, 'Barista')

    def test_get_checkin_in_barista_is_checked_in(self):
        barista_list = self.company_location.get_checkin_in()
        for barista in barista_list:
            self.assertEquals(True, self.baristadetails.usercheckedin)

class UserProfileManagerTest(TestCase):

    def setUp(self):
        create_user_and_details(
            username='chris', 
            password='bagel', 
            email='chrisvanschyndel@gmail.com', 
            first_name='chris', 
            last_name='van schyndel', 
            mug='U1.jpg', 
            favCompany=None, 
            favBaristaObj=None
            )
        self.client = Client()
        self.user = User.objects.get(username='chris')

    def test_check_in_user_checks_in_user(self):
        UserProfile.objects.check_in_user(self.user, self.client)
        userdetails = self.user.get_profile()
        self.assertEquals(userdetails.usercheckedin, True)

    def test_check_in_user_saves_user_checkinflag(self):
        UserProfile.objects.check_in_user(self.user, self.client)
        userdetails = self.user.get_profile()
        self.assertEquals(userdetails.usercheckedin, User.objects.get(username=self.user.username).get_profile().usercheckedin)

class UserAndUserProfileTest(TestCase):

    def setUp(self):
        create_company_and_associated_location(
            companyName="Voltage", 
            companyContact="Lucy", 
            street="275 3rd street", 
            city="Cambridge", 
            state="Massachusetts", 
            zipCode="21432"
            )
        self.company = Company.objects.get(companyName="Voltage")
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
        create_barista_and_details(
            username='quayle', 
            password='popcorn', 
            email='leanqueen@bagel.com', 
            usercheckedin=False, 
            first_name='quayle', 
            last_name='the brave', 
            mug='whileawayflowers.jpg'
            )
        self.barista2 = User.objects.get(username='quayle')
        self.barista2details = self.barista2.get_profile()
        create_checkin_and_association(barista=self.barista2, company=self.company, checkedin=False)
        self.checkin2 = checkIn.objects.get(barista=self.barista2)
        create_user_and_details(
            username='aprice', 
            password='bagel', 
            email='aprice@gmail.com', 
            first_name='andrew', 
            last_name='price', 
            mug='gargamel.jpg', 
            favCompany=self.company, 
            favBaristaObj=self.barista2details
            )
        self.user2 = User.objects.get(username='aprice')
        self.user2details = self.user2.get_profile()

    def test_unicode(self):
        self.assertEquals(type(u'a'), type(self.user.__unicode__()))

    def test_unicode_for_userprofile(self):
        self.assertEquals(type(u'a'), type(self.userdetails.__unicode__()))

    def test_show_user_returns_unicode(self):
        self.assertEquals(type(self.userdetails.showUser()), type(u'a'))

    def test_isfavbarcheckedin_returns_false_on_empty_field(self):
        self.assertEquals(type(self.baristadetails.isFavBarCheckedIn()), type(False))

    def test_isfavbarcheckedin_returns_true_if_favbarista_checkedin(self):
        self.assertEquals(type(self.userdetails.isFavBarCheckedIn()), type(True))

    def test_isfavbarcheckedin_returns_false_if_favbarista_checkedout(self):
        self.assertEquals(type(self.user2details.isFavBarCheckedIn()), type(False))

    def test_get_fav_bar_checked_in_returns_checkIn_obj(self):
        self.assertEquals(type(self.userdetails.get_favBarCheckIn()), type(checkIn()))

    def test_update_favs_updates_favBarista_properly(self):
        self.userdetails.update_favs(False, self.baristadetails.id)
        self.assertEquals(self.userdetails.favBaristaObj, self.baristadetails)

    def test_update_favs_updates_favCompany_properly(self):
        self.userdetails.update_favs(self.company.id, False)
        self.assertEquals(self.userdetails.favCompany, self.company)

    def test_get_mug_returns_mug_when_it_exists(self):
        self.userdetails.mug = 'cheesecake.jpg'
        self.assertEquals(self.userdetails.get_mug(), 'cheesecake.jpg')

    def test_get_mug_returns_default_image_when_it_doesnt_exist(self):
        self.userdetails.mug = 'U1.jpg'
        self.assertEquals(self.userdetails.get_mug(), None)

    def test_get_self_checkin_success_returns_user(self):
        self.assertEquals(self.baristadetails.get_self_checkIn(), checkIn.objects.get(barista=self.barista))

    def test_get_self_checkin_fail_returns_None(self):
        self.assertEquals(self.userdetails.get_self_checkIn(), None)

    def test_get_favorite_company_id_returns_favCompany(self):
        self.assertEquals(self.userdetails.get_favorite_company_id(), self.userdetails.favCompany.id)

    def test_get_favorite_company_id_returns_0string(self):
        self.assertEquals(self.baristadetails.get_favorite_company_id(), '0')

class checkInTest(TestCase):

    def setUp(self):
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
        create_checkin_and_association(barista=self.barista, company=self.company, checkedin=True)
        self.checkin = checkIn.objects.get(barista=self.barista)
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
        create_barista_and_details(
            username='quayle', 
            password='popcorn', 
            email='leanqueen@bagel.com', 
            usercheckedin=False, 
            first_name='quayle', 
            last_name='the brave', 
            mug='whileawayflowers.jpg'
            )
        self.barista2 = User.objects.get(username='quayle')
        self.barista2details = self.barista2.get_profile()
        create_checkin_and_association(barista=self.barista2, company=self.company, checkedin=False)
        self.checkin2 = checkIn.objects.get(barista=self.barista2)

    def test_unicode_checked_in_fork(self):
        self.assertEquals(type(u'a'), type(self.checkin.__unicode__()))

    def test_unicode_checked_out_fork(self):
        self.assertEquals(type(u'a'), type(self.checkin2.__unicode__()))

    def test_show_barista_returns_unicode(self):
        self.assertEquals(type(u'a'), type(self.checkin.showBarista()))

    def test_get_barista_mug_returns_mug(self): 
        self.assertEquals(self.checkin.get_barista_mug(), 'abra.jpg')

    def test_get_tzobject_returns_datetime_object_checkin_true_fork(self):
        self.assertEquals(type(self.checkin.get_tzobject()), type(timezone.now()))

    def test_get_tzobject_returns_datetime_object_checkin_false_fork(self):
        self.assertEquals(type(self.checkin2.get_tzobject()), type(timezone.now()))

    def test_check_out_user_changes_checkedin_state(self):    
        self.checkin.check_out_user()
        self.assertEquals(checkIn.objects.get(barista=User.objects.get(username='jimmy')).checkedin, False)



