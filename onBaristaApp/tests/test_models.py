from django.utils import unittest
from django.test import TestCase
from onBaristaApp.models import User, checkIn, companyLocation, Company, UserProfile, UserProfileManager

class CompanyTest(TestCase):

    def setUp(self):
        pass

    def test_unicode(self):
      
    def test_get_locations_returns_query(self):

    def test_get_locations_query_has_companyLocation_object(self):

class CompanyLocationTest(TestCase):

    def setUp(self):
        pass

    def test_unicode(self):

    def test_address_string_returns_string(self):

    def test_get_checkins_returns_query(self):

    def test_get_checkins_query_has_checkIn_object(self):

    def test_get_checkin_out_returns_list(self):

    def test_get_checkin_out_list_has_checkIn_object(self):

    def test_get_checkin_in_returns_list(self):

    def test_get_checkin_in_list_has_checkIn_object(self):

class UserProfileManagerTest(TestCase):

    def setUp(self):
        pass

    def test_check_in_user_checks_in_user(self):

    def test_check_in_user_saves_user(self):

class UserAndUserProfileTest(TestCase):

    def setUp(self):
        pass

    def test_unicode(self):

    def test_show_user_returns_string(self):

    def test_isfavbarcheckedin_returns_boolean(self):

    def test_get_fav_bar_checked_in_returns_user(self):

    def test_update_favs_updates_favBarista_properly(self):

    def test_update_favs_updates_favCompany_properly(self):

    def test_get_mug_returns_mug(self):

    def test_get_self_checkin_returns_user(self):

    def test_get_self_checkin_returns_None(self):

class checkInTest(TestCase):

    def setUp(self):
        pass

    def test_unicode(self):

    def test_show_barista_returns_string(self):

    def test_get_barista_mug_returns_mug(self):

    def test_get_tzobject_returns_datetime_object(self):

    def test_check_out_user_changes_checkedin_state(self):

    def test_check_out_user_saves_user(self):

    def test_check_out_user_saves_userdetails_profile(self):



