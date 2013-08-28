from django.utils import unittest
from django.test import TestCase
from onBaristaApp.models import User, checkIn, companyLocation, Company, UserProfile, UserProfileManager

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
        pass

    def test_unicode(self):
        pass

    def test_address_string_returns_string(self):
        pass

    def test_get_checkins_returns_query(self):
        pass

    def test_get_checkins_query_has_checkIn_object(self):
        pass

    def test_get_checkin_out_returns_list(self):
        pass

    def test_get_checkin_out_list_has_checkIn_object(self):
        pass

    def test_get_checkin_in_returns_list(self):
        pass

    def test_get_checkin_in_list_has_checkIn_object(self):
        pass

class UserProfileManagerTest(TestCase):

    def setUp(self):
        pass

    def test_check_in_user_checks_in_user(self):
        pass

    def test_check_in_user_saves_user(self):
        pass

class UserAndUserProfileTest(TestCase):

    def setUp(self):
        pass

    def test_unicode(self):
        pass

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
        pass

    def test_unicode(self):
        pass

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



