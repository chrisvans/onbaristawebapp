from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.contrib.auth import authenticate
from django.http import HttpResponse
import datetime

# Create your models here.



class Company(models.Model):
	companyName = models.CharField(max_length=200)
	companyContact = models.CharField(max_length=200)
	def __unicode__(self):
		return self.companyName
	def get_locations(self):
		return companyLocation.objects.filter(companyID = self)

class companyLocation(models.Model):
	checkins = {}
	companyID = models.ForeignKey(Company)
	street = models.CharField(max_length=200, blank=True)
	city = models.CharField(max_length= 20, blank=True)

	state_choices = (
			('MA', 'Massachusetts'),
			('CT', 'Connecticut'),
			('NH', 'New Hampshire'),
			('VT', 'Vermont'),
			('ME', 'Maine'),
		)
	state = models.CharField(max_length=2,
							choices = state_choices,
							default='MA', blank=True)
	zipCode= models.CharField(max_length= 5, blank=True)

	def address_string(self):
		address = self.street + ", " + self.city + ", " + self.state + " " + self.zipCode
		return address

	def __unicode__(self):
		return self.address_string()
	def get_checkins(self):
		return checkIn.objects.filter(location = self)
	#def checkout(self, barista):
	#	print self.checkins
	#	del self.checkins[barista]

## Anthony's previous User Model
#class User(models.Model):
#	userName = models.CharField(max_length=20)
#	password = models.CharField(max_length=20)
#	user_type_choices = (
#		('Barista', 'Barista'),
#		('Consumer', 'Consumer'),
#	) 
#	userType = models.CharField(max_length=10,
#								choices=user_type_choices,
#								default='Consumer')
#	firstName = models.CharField(max_length=30)
#	lastName = models.CharField(max_length=30)
#	favCompany = models.ForeignKey(Company, null=True, blank=True)
#	favBaristaObj = models.ForeignKey('self', null=True, blank=True)
#
#	def __unicode__(self):
#		personDesc = self.userType + ": " + self.firstName + " " + self.lastName
#		return personDesc
#	def showUser(self):
#		personDesc = self.userType + ": " + self.firstName + " " + self.lastName
#		return personDesc

# Django User model
# class models.User
# Comes with username, password, first_name, last_name, 
# last_login, and date_joined - as well as check_password(raw_password) and set_password(raw_password)
# Also has group permissions - Will want to use these for Barista-Consumer relationship

# Django UserManager model
# class models.UserManager
# Comes with create_user(username, email=None, password=None) and make_random_password(length=10)

class UserProfile(models.Model):
	user = models.OneToOneField(User)
	#full_name =user.get_full_name()
	# Use 'User'.get_profile().userType to get the userType, for example
	full_name=models.CharField(max_length=50, default='', null=True, blank=True)
	user_type_choices = (
		('Barista', 'Barista'),
		('Consumer', 'Consumer'),
		)
	userType = models.CharField(max_length=10, choices=user_type_choices, default='Consumer')
	favCompany = models.ForeignKey(Company, null=True, blank=True)
	favBaristaObj = models.ForeignKey('self', null=True, blank=True)
	def __unicode__(self):
		return self.userType + ": " + self.user.first_name + " " + self.user.last_name
	#def showUser(self):
	#	return user.userType + ": " + user.first_name + " " + user.last_name

def create_user_profile(sender, instance, created, **kwargs):

	# print "instance: " + str(instance)
	# print " kwargs: " + str(kwargs)
	# print "create up 1: " + instance.get_full_name()
	name = instance.get_full_name()
	if name:
		profile = instance.get_profile()
		profile.full_name = name
		profile.save()
	if created:
		#UserProfile.objects.create(user=instance)
		up = UserProfile()
		up.full_name = instance.first_name + " " + instance.last_name
		up.user = instance
		up.save()
		#print "in create user profile: "  + up.full_name


post_save.connect(create_user_profile, sender=User)


class checkIn(models.Model):
	barista = models.ForeignKey(User)
	location = models.ForeignKey(companyLocation)
	inTime = models.DateTimeField()
	outTime = models.DateTimeField(null=True)
	def __unicode__(self):
		#baristadetails = self.barista.get_profile()
		#showUser = baristadetails.userType + ": " + self.barista.first_name + " " + self.barista.last_name
		checkinDesc = showUser(self.barista) + " at " + unicode(self.inTime)
		return checkinDesc

#class checkOut(models.Model):
#	barista = models.ForeignKey(User)
#	location = models.ForeignKey(companyLocation)
	#inTime = models.DateTimeField()
#	outTime = models.DateTimeField()
#	def __unicode__(self):
#		checkoutDesc = showUser(self.barista) + " at " + unicode(self.outTime)
#		return checkoutDesc

# If we can find a way to make UserProfile reference the same corresponding 
# User class, this could be a method within UserProfile.
def showUser(Userobject):
	user = Userobject
	userdetails = Userobject.get_profile()
	return userdetails.userType + ": " + user.first_name + " " + user.last_name




