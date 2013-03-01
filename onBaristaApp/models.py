from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.contrib.auth import authenticate
from django.http import HttpResponse
import datetime

# Create your models here.



class Company(models.Model):
	companyName = models.CharField(max_length=200)
	companyContact = models.CharField(max_length=200, blank=True)
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
		address = self.companyID.companyName + ": " + self.street + ", " + self.city + ", " + self.state + " " + self.zipCode
		return address

	def __unicode__(self):
		return self.address_string()
	def get_checkins(self):
		return checkIn.objects.filter(location = self)
	def get_checkin_out(self):
		# Method returns all checked out baristas at this location
		bagel = checkIn.objects.filter(location = self)
		barista_list = []
		for bagels in bagel:
			if bagels.checkedin == False:
				barista = bagels.barista
				barista_list.append(barista)
		return barista_list
	def get_checkin_in(self):
		# Method returns all checked in baristas at this location
		bagel = checkIn.objects.filter(location = self)
		barista_list = []
		for bagels in bagel:
			if bagels.checkedin == True:
				barista = bagels.barista
				barista_list.append(barista)
		return barista_list

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
	mug = models.FileField(upload_to='Mugs')
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
	usercheckedin = models.BooleanField(default=False)
	def __unicode__(self):
		return self.userType + ": " + self.user.first_name + " " + self.user.last_name
	def showUser(self):
		return self.userType + ": " + self.user.first_name + " " + self.user.last_name
	def isFavBarCheckedIn(self):
		# Returns true if this user's favorite barista is checked in.
		if self.favBaristaObj:
			checkInObj = checkIn.objects.get(barista = self.favBaristaObj.user)
			if checkInObj and checkInObj.checkedin:
				return True
		return False
	def get_favBarCheckIn(self):
		# Returns the favorite barista's user object if it exists, otherwise returns an empty string.
		if self.favBaristaObj:
			try:
				checkIn.objects.get(barista = self.favBaristaObj.user)
				return checkIn.objects.get(barista = self.favBaristaObj.user)
			except (KeyError,checkIn.DoesNotExist):
				return 'error'
	def update_favs(self, companyID, baristaID):
		if baristaID:
			baristaObj = UserProfile.objects.get(pk=baristaID)
			self.favBaristaObj = baristaObj
		if companyID:
			companyObj = Company.objects.get(pk=companyID)
			self.favCompany = companyObj
		self.save()

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
	inTime = models.DateTimeField(null=True)
	outTime = models.DateTimeField(null=True)
	checkedin = models.BooleanField(default=True)
	def showBarista(self):
		user = self.barista
		userdetails = self.barista.get_profile()
		return user.first_name + " " + user.last_name
	def __unicode__(self):
		#baristadetails = self.barista.get_profile()
		#showUser = baristadetails.userType + ": " + self.barista.first_name + " " + self.barista.last_name
		uniInTime = str(self.inTime)
		uniInTime = uniInTime[0:16]
		uniOutTime = str(self.outTime)
		uniOutTime = uniOutTime[0:16]
		baristadetails = self.barista.get_profile()
		if self.checkedin:
			checkinDesc = self.showBarista() + " checked in at " + unicode(uniInTime)
		else:
			checkinDesc = self.showBarista() + " checked out at " + unicode(uniOutTime)
		return checkinDesc

# Possible use of dictionary in the database.
#class Dicty(models.Model):
#	name = models.CharField(max_length=25)

#class KeyVal(models.Model):
#	container = models.ForeignKey(Dicty, db_index=True)
#	key = models.CharField(max_length=240, db_index=True)
#	value = models.CharField(max_length=240, db_index=True)




