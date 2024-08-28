from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(Messcut)
class MesscutAdmin(admin.ModelAdmin):
	list_display = ['start_date','end_date']
	list_filter = ['start_date','end_date']
	search_fields = ['start_date','end_date']
	list_per_page = 10

@admin.register(Messmenu)
class MessmenuAdmin(admin.ModelAdmin):
	list_display = ['day','breakfast','lunch','dinner']
	list_filter = ['day','breakfast','lunch','dinner']
	search_fields = ['day','breakfast','lunch','dinner']
	list_per_page = 10





@admin.register(MessAttendance)
class MessAttendanceAdmin(admin.ModelAdmin):
	list_display = ['meal','student','timestamp']
	list_filter = ['meal','student','timestamp']
	search_fields = ['meal','student','timestamp']

@admin.register(MessBill)
class MessBillAdmin(admin.ModelAdmin):
	list_display = ['amount','month','paid']
	list_filter = ['amount','month','paid']
	search_fields = ['amount','month','paid']


@admin.register(Messsettings)
class MesssettingsAdmin(admin.ModelAdmin):
	list_display = ['total_days','amount_per_day','establishment_charges','feast_charges','other_charges']
	list_filter = ['total_days','amount_per_day','establishment_charges','feast_charges','other_charges']
	search_fields = ['total_days','amount_per_day','establishment_charges','feast_charges','other_charges']
	list_per_page = 10