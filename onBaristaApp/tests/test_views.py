from django.utils import unittest
from django.test import TestCase
from django.utils import timezone
from django.utils.timezone import utc, get_current_timezone, activate, localtime
from django.test.client import Client
from onBaristaApp.models import User, checkIn, companyLocation, Company, UserProfile, UserProfileManager
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

def get_all_urls():
    return ['/',
            '/logout/',
            '/checkIn',
            '/checkOut/',
            '/baristas/',
            '/baristasCheck/',
            '/favorites/',
            '/updateFavs/',
            '/baristaList/',
            '/companyList/',
            '/register/',
            # This view requires a company ID and will need to have a valid company, set to 1 here.
            '/home/1/',
            '/home/',
            '/Profile/',
            '/AdminPanel/'
            ]

class BroadViewTest(TestCase):

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