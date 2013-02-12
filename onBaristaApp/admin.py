from django.contrib import admin
from onBaristaApp.models import Company, companyLocation, User, checkIn
from django.contrib.auth import authenticate

class locationInLine(admin.TabularInline):
	model = companyLocation

class companyAdmin(admin.ModelAdmin):
	fieldsets = [
			(None, {'fields':['companyName', 'companyContact']})
	]
	inlines = [locationInLine]

admin.site.register(Company, companyAdmin)
admin.site.register((companyLocation, checkIn))