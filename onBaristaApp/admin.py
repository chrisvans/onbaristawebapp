from django.contrib import admin
from onBaristaApp.models import Company, companyLocation, User, checkIn

class locationInLine(admin.TabularInline):
	model = companyLocation

class companyAdmin(admin.ModelAdmin):
	fieldsets = [
			(None, {'fields':['companyName', 'companyContact']})
	]
	inlines = [locationInLine]

admin.site.register(Company, companyAdmin)
admin.site.register((User, companyLocation, checkIn))