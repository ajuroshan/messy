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
	list_display = ['date','breakfast','lunch','dinner']
	list_filter = ['date','breakfast','lunch','dinner']
	search_fields = ['date','breakfast','lunch','dinner']
	list_per_page = 10


@admin.register(MessAttendance)
class MessAttendanceAdmin(admin.ModelAdmin):
	list_display = ['meal','student','timestamp']
	list_filter = ['meal','student','timestamp']
	search_fields = ['meal','student','timestamp']
