from django.db import models

# Create your models here.



class Company(models.Model):
	companyName = models.CharField(max_length=200)
	companyContact = models.CharField(max_length=200)
	def __unicode__(self):
		return self.companyName
	def get_locations(self):
		return companyLocation.objects.filter(companyID = self)

class companyLocation(models.Model):
	companyID = models.ForeignKey(Company)
	street = models.CharField(max_length=200)
	city = models.CharField(max_length= 20)

	state_choices = (
			('Ma', 'Massachusetts'),
			('CT', 'Connecticut'),
			('NH', 'New Hampshire'),
			('VT', 'Vermont'),
			('ME', 'Maine'),
		)
	state = models.CharField(max_length=2,
							choices = state_choices,
							default='Ma')
	zipCode= models.CharField(max_length= 5)

	def address_string(self):
		address = self.street + ", " + self.city + ", " + self.state + " " + self.zipCode
		return address

	def __unicode__(self):
		return self.address_string()

class User(models.Model):
	userName = models.CharField(max_length=20)
	password = models.CharField(max_length=20)
	user_type_choices = (
		('Barista', 'Barista'),
		('Consumer', 'Consumer'),
	) 
	userType = models.CharField(max_length=10,
								choices=user_type_choices,
								default='Consumer')
	firstName = models.CharField(max_length=30)
	lastName = models.CharField(max_length=30)
	favCompany = models.ForeignKey(Company)
	favBarista = models.IntegerField() #???? this might not work -- since it's possibly not "foreign"

	def __unicode__(self):
		personDesc = self.userType + ": " + self.firstName + " " + self.lastName
		return personDesc
	def showUser(self):
		personDesc = self.userType + ": " + self.firstName + " " + self.lastName
		return personDesc

class checkIn(models.Model):
	barista = models.ForeignKey(User)
	location = models.ForeignKey(companyLocation)
	inTime = models.DateField()
	outTime = models.DateField()
	def __unicode__(self):
		checkinDesc = self.barista.showUser() + " at " + self.location.address_string()
		return checkinDesc