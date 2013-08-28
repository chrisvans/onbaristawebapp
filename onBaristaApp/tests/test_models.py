from django.utils import unittest
from django.test import TestCase
from onBaristaApp.models import User, checkIn, companyLocation, Company, UserProfile, UserProfileManager
from django.utils import timezone
from django.utils.timezone import utc, get_current_timezone, activate, localtime
from django.test.client import Client
import datetime

def create_company_and_associated_location(companyName, companyContact, street, city, state, zipCode):
    company = Company.objects.create(companyName=companyName, companyContact=companyContact)
    companyLocation.objects.create(companyID=company, street=street, city=city, state=state, zipCode=zipCode)

def create_barista_and_details(username, password, email, usercheckedin, first_name, last_name, mug):
    barista = User(username=username, password=password, email=email)
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
        create_company_and_associated_location(companyName="Voltage", companyContact="Lucy", street="275 3rd street", city="Cambridge", state="Massachusetts", zipCode="21432")

    def test_unicode(self):
        self.assertEquals(type(u'a'), type(Company.objects.all()[0].__unicode__()))
      
    def test_get_locations_returns_query(self):
        queryset = Company.objects.all()[0].get_locations()
        self.assertEquals(type(Company.objects.all()), type(queryset))

    def test_get_locations_query_has_companyLocation_object(self):
        type_check = type(companyLocation.objects.all()[0])
        queryset = Company.objects.all()[0].get_locations()
        for location in queryset:
            self.assertEquals(type_check, type(location))


class CompanyLocationTest(TestCase):

    def setUp(self):
        create_company_and_associated_location(companyName="Voltage", companyContact="Lucy", street="275 3rd street", city="Cambridge", state="Massachusetts", zipCode="21432")
        company = Company.objects.all()[0]
        create_barista_and_details(username='jimmy', password='popcorn', email='jimmydean@bagel.com', usercheckedin=True, first_name='jimmy', last_name='dean', mug='abra.jpg')
        barista = User.objects.get(username='jimmy')
        create_checkin_and_association(barista=barista, company=company, checkedin=True)
        create_barista_and_details(username='quayle', password='popcorn', email='leanqueen@bagel.com', usercheckedin=False, first_name='quayle', last_name='the brave', mug='whileawayflowers.jpg')
        barista2 = User.objects.get(username='quayle')
        create_checkin_and_association(barista=barista2, company=company, checkedin=False)

    def test_unicode(self):
        self.assertEquals(type(u'a'), type(companyLocation.objects.all()[0].__unicode__()))

    def test_address_string_returns_unicode(self):
        companylocation = companyLocation.objects.all()[0]
        self.assertEquals(type(u'a'), type(companylocation.address_string()))

    def test_get_checkins_returns_query(self):
        companylocation = companyLocation.objects.all()[0]
        self.assertEquals(type(Company.objects.all()), type(companylocation.get_checkins()))

    def test_get_checkins_query_has_checkIn_object(self):
        companylocation = companyLocation.objects.all()[0]
        checkinsquery = companylocation.get_checkins()
        for checkin in checkinsquery:
            self.assertEquals(type(checkIn()), type(checkin))

    def test_get_checkin_out_returns_list(self):
        companylocation = companyLocation.objects.all()[0]
        barista_list = companylocation.get_checkin_out()
        self.assertEquals(type(barista_list), type([]))

    def test_get_checkin_out_list_has_baristas(self):
        companylocation = companyLocation.objects.all()[0]
        barista_list = companylocation.get_checkin_out()
        for barista in barista_list:
            baristadetails = barista.get_profile()
            self.assertEquals(baristadetails.userType, 'Barista')

    def test_get_checkin_out_barista_is_checked_out(self):
        companylocation = companyLocation.objects.all()[0]
        barista_list = companylocation.get_checkin_out()
        for barista in barista_list:
            baristadetails = barista.get_profile()
            self.assertEquals(False, baristadetails.usercheckedin)

    def test_get_checkin_in_returns_list(self):
        companylocation = companyLocation.objects.all()[0]
        barista_list = companylocation.get_checkin_in()
        self.assertEquals(type(barista_list), type([]))

    def test_get_checkin_in_list_has_baristas(self):
        companylocation = companyLocation.objects.all()[0]
        barista_list = companylocation.get_checkin_out()
        for barista in barista_list:
            baristadetails = barista.get_profile()
            self.assertEquals(baristadetails.userType, 'Barista')

    def test_get_checkin_in_barista_is_checked_in(self):
        companylocation = companyLocation.objects.all()[0]
        barista_list = companylocation.get_checkin_in()
        for barista in barista_list:
            baristadetails = barista.get_profile()
            self.assertEquals(True, baristadetails.usercheckedin)

class UserProfileManagerTest(TestCase):

    def setUp(self):
        create_user_and_details(username='chris', password='bagel', email='chrisvanschyndel@gmail.com', first_name='chris', last_name='van schyndel', mug='U1.jpg', favCompany=None, favBaristaObj=None)

    def test_check_in_user_checks_in_user(self):
        client = Client()
        user = User.objects.all()[0]
        UserProfile.objects.check_in_user(user, client)
        userdetails = user.get_profile()
        self.assertEquals(userdetails.usercheckedin, True)

    def test_check_in_user_saves_user_checkinflag(self):
        client = Client()
        user = User.objects.all()[0]
        UserProfile.objects.check_in_user(user, client)
        userdetails = user.get_profile()
        self.assertEquals(userdetails.usercheckedin, User.objects.get(username=user.username).get_profile().usercheckedin)

class UserAndUserProfileTest(TestCase):

    def setUp(self):
        create_company_and_associated_location(companyName="Voltage", companyContact="Lucy", street="275 3rd street", city="Cambridge", state="Massachusetts", zipCode="21432")
        company = Company.objects.all()[0]
        create_barista_and_details(username='jimmy', password='popcorn', email='jimmydean@bagel.com', usercheckedin=True, first_name='jimmy', last_name='dean', mug='abra.jpg')
        barista = User.objects.get(username='jimmy')
        create_user_and_details(username='chris', password='bagel', email='chrisvanschyndel@gmail.com', first_name='chris', last_name='van schyndel', mug='U1.jpg', favCompany=company, favBaristaObj=barista.get_profile())
        create_checkin_and_association(barista=barista, company=company, checkedin=True)

    def test_unicode(self):
        self.assertEquals(type(u'a'), type(User.objects.all()[0].__unicode__()))

    def test_show_user_returns_unicode(self):
        user = User.objects.all()[0]
        userdetails = user.get_profile()
        self.assertEquals(type(userdetails.showUser()), type(u'a'))

    def test_isfavbarcheckedin_returns_boolean(self):
        userdetails = User.objects.all()[0].get_profile()
        self.assertEquals(type(userdetails.isFavBarCheckedIn()), type(False))

    def test_get_fav_bar_checked_in_returns_checkIn_obj(self):
        userdetails = User.objects.filter(username='chris')[0].get_profile()
        self.assertEquals(type(userdetails.get_favBarCheckIn()), type(checkIn()))

    def test_update_favs_updates_favBarista_properly(self):
        barista = User.objects.get(username='jimmy')
        baristadetails = barista.get_profile()
        userdetails = User.objects.all()[0].get_profile()
        userdetails.update_favs(False, baristadetails.id)
        self.assertEquals(userdetails.favBaristaObj, baristadetails)

    def test_update_favs_updates_favCompany_properly(self):
        company = Company.objects.all()[0]
        userdetails = User.objects.all()[0].get_profile()
        userdetails.update_favs(company.id, False)
        self.assertEquals(userdetails.favCompany, company)

    def test_get_mug_returns_mug(self):
        user = User.objects.all()[0]
        userdetails = user.get_profile()
        userdetails.mug = "cheesecake.jpg"
        self.assertEquals(userdetails.get_mug(), "cheesecake.jpg")

    def test_get_self_checkin_success_returns_user(self):
        user = User.objects.get(username='jimmy')
        userdetails = user.get_profile()
        self.assertEquals(userdetails.get_self_checkIn(), checkIn.objects.get(barista=user))

    def test_get_self_checkin_fail_returns_None(self):
        user = User.objects.get(username='chris')
        userdetails = user.get_profile()
        self.assertEquals(userdetails.get_self_checkIn(), None)

    def test_get_favorite_company_id_returns_favCompany(self):
        user = User.objects.get(username='chris')
        userdetails = user.get_profile()
        self.assertEquals(userdetails.get_favorite_company_id(), userdetails.favCompany.id)

    def test_get_favorite_company_id_returns_0string(self):
        user = User.objects.get(username='jimmy')
        userdetails = user.get_profile()
        self.assertEquals(userdetails.get_favorite_company_id(), '0')

class checkInTest(TestCase):

    def setUp(self):
        create_company_and_associated_location(companyName="Voltage", companyContact="Lucy", street="275 3rd street", city="Cambridge", state="Massachusetts", zipCode="21432")
        company = Company.objects.all()[0]
        create_barista_and_details(username='jimmy', password='popcorn', email='jimmydean@bagel.com', usercheckedin=True, first_name='jimmy', last_name='dean', mug='abra.jpg')
        barista = User.objects.get(username='jimmy')
        create_user_and_details(username='chris', password='bagel', email='chrisvanschyndel@gmail.com', first_name='chris', last_name='van schyndel', mug='U1.jpg', favCompany=company, favBaristaObj=barista.get_profile())
        create_checkin_and_association(barista=barista, company=company, checkedin=True)

    def test_unicode(self):
        self.assertEquals(type(u'a'), type(checkIn.objects.all()[0].__unicode__()))

    def test_show_barista_returns_unicode(self):
        checkin = checkIn.objects.all()[0]
        self.assertEquals(type(u'a'), type(checkin.showBarista()))

    def test_get_barista_mug_returns_mug(self):
        checkin = checkIn.objects.get(location=companyLocation.objects.get(companyID=1))
        self.assertEquals(checkin.get_barista_mug(), 'abra.jpg')

    def test_get_tzobject_returns_datetime_object(self):
        checkin = checkIn.objects.get(location=companyLocation.objects.get(companyID=1))
        self.assertEquals(type(checkin.get_tzobject()), type(timezone.now()))

    def test_check_out_user_changes_checkedin_state(self):
        checkin = checkIn.objects.get(location=companyLocation.objects.get(companyID=1))        
        checkin.check_out_user()
        self.assertEquals(checkIn.objects.get(location=companyLocation.objects.get(companyID=1)).checkedin, False)



