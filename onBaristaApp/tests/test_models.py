from django.utils import unittest
from django.test import TestCase
from onBaristaApp.models import User, checkIn, companyLocation, Company, UserProfile, UserProfileManager
from django.utils import timezone
from django.utils.timezone import utc, get_current_timezone, activate, localtime
import datetime

class CompanyTest(TestCase):

    def setUp(self):
        company = Company.objects.create(companyName="Voltage", companyContact="Lucy")
        location = companyLocation.objects.create(companyID=company, street="275 3rd street", city="Cambridge", state="Massachusetts", zipCode="21432")

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
        company = Company.objects.create(companyName="Voltage", companyContact="Lucy")
        location = companyLocation.objects.create(companyID=company, street="275 3rd street", city="Cambridge", state="Massachusetts", zipCode="21432")
        barista = User(username='jimmy', password='popcorn', email='jimmydean@bagel.com')
        barista.save()
        baristadetails = barista.get_profile()
        baristadetails.userType = 'Barista'
        baristadetails.usercheckedin = True
        baristadetails.first_name='jimmy'
        baristadetails.last_name='dean'
        barista.save()
        baristadetails.save()
        checkin = checkIn()
        checkin.barista = User.objects.get(username=barista.username)
        checkin.location = companyLocation.objects.get(companyID=company)
        checkin.inTime = timezone.now()
        checkin.outTime = timezone.now()
        checkin.save()
        barista2 = User(username='quayle', password='popcorn', email='leanqueen@bagel.com')
        barista2.save()
        barista2details = barista.get_profile()
        barista2details.userType = 'Barista'
        barista2details.usercheckedin = False
        barista2details.first_name='quayle'
        barista2details.last_name='the brave'
        barista2.save()
        barista2details.save()
        checkin2 = checkIn()
        checkin2.barista = User.objects.get(username=barista2.username)
        checkin2.location = companyLocation.objects.get(companyID=company)
        checkin2.inTime = timezone.now()
        checkin2.outTime = timezone.now()
        checkin2.save()

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
            self.assertEquals(barista.userType, 'Barista')

    def test_get_checkin_out_barista_is_checked_out(self):
        companylocation = companyLocation.objects.all()[0]
        barista_list = companylocation.get_checkin_in()
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
            self.assertEquals(barista.userType, 'Barista')

    def test_get_checkin_in_barista_is_checked_in(self):
        companylocation = companyLocation.objects.all()[0]
        barista_list = companylocation.get_checkin_out()
        for barista in barista_list:
            baristadetails = barista.get_profile()
            self.assertEquals(True, baristadetails.usercheckedin)

class UserProfileManagerTest(TestCase):

    def setUp(self):
        pass

    def test_check_in_user_checks_in_user(self):
        pass

    def test_check_in_user_saves_user(self):
        pass

class UserAndUserProfileTest(TestCase):

    def setUp(self):
        company = Company.objects.create(companyName="Voltage", companyContact="Lucy")
        location = companyLocation.objects.create(companyID=company, street="275 3rd street", city="Cambridge", state="Massachusetts", zipCode="21432")
        user = User(username='chris', password='bagel', email='chrisvanschyndel@gmail.com')
        user.save()
        userdetails = user.get_profile()
        userdetails.mug = 'U1.jpg'
        userdetails.first_name='chris'
        userdetails.last_name='van schyndel'
        user.save()
        userdetails.save()
        barista = User(username='jimmy', email='jimmydean@bagel.com')
        barista.save()
        baristadetails = barista.get_profile()
        baristadetails.userType = 'Barista'
        baristadetails.usercheckedin = True
        baristadetails.first_name='jimmy'
        baristadetails.last_name='dean'
        barista.save()
        baristadetails.save()
        checkin = checkIn()
        checkin.barista = User.objects.get(username=barista.username)
        checkin.location = companyLocation.objects.get(companyID=company)
        checkin.inTime = timezone.now()
        checkin.outTime = timezone.now()
        checkin.save()

    def test_unicode(self):
        self.assertEquals(type(u'a'), type(User.objects.all()[0].__unicode__()))

    def test_show_user_returns_string(self):
        pass

    def test_isfavbarcheckedin_returns_boolean(self):
        pass

    def test_get_fav_bar_checked_in_returns_user(self):
        pass

    def test_update_favs_updates_favBarista_properly(self):
        pass

    def test_update_favs_updates_favCompany_properly(self):
        pass

    def test_get_mug_returns_mug(self):
        pass

    def test_get_self_checkin_returns_user(self):
        pass

    def test_get_self_checkin_returns_None(self):
        pass

class checkInTest(TestCase):

    def setUp(self):
        company = Company.objects.create(companyName="Voltage", companyContact="Lucy")
        location = companyLocation.objects.create(companyID=company, street="275 3rd street", city="Cambridge", state="Massachusetts", zipCode="21432")
        user = User(username='chris', password='bagel', email='chrisvanschyndel@gmail.com')
        user.save()
        userdetails = user.get_profile()
        userdetails.mug = 'U1.jpg'
        userdetails.first_name='chris'
        userdetails.last_name='van schyndel'
        user.save()
        userdetails.save()
        barista = User(username='jimmy', email='jimmydean@bagel.com')
        barista.save()
        baristadetails = barista.get_profile()
        baristadetails.userType = 'Barista'
        baristadetails.usercheckedin = True
        baristadetails.first_name='jimmy'
        baristadetails.last_name='dean'
        barista.save()
        baristadetails.save()
        checkin = checkIn()
        checkin.barista = User.objects.get(username=barista.username)
        checkin.location = companyLocation.objects.get(companyID=company)
        checkin.inTime = timezone.now()
        checkin.outTime = timezone.now()
        checkin.save()

    def test_unicode(self):
        self.assertEquals(type(u'a'), type(checkIn.objects.all()[0].__unicode__()))

    def test_show_barista_returns_string(self):
        pass

    def test_get_barista_mug_returns_mug(self):
        pass

    def test_get_tzobject_returns_datetime_object(self):
        pass

    def test_check_out_user_changes_checkedin_state(self):
        pass

    def test_check_out_user_saves_user(self):
        pass

    def test_check_out_user_saves_userdetails_profile(self):
        pass



