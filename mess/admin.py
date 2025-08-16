from django.contrib import admin
from .models import *
from django.contrib import admin
from application.models import Hostel

@admin.register(Messcut)
class MesscutAdmin(admin.ModelAdmin):
	list_display = ['start_date', 'end_date']
	list_filter = ['start_date', 'end_date']
	search_fields = ['start_date', 'end_date']
	list_per_page = 10


@admin.register(Messmenu)
class MessmenuAdmin(admin.ModelAdmin):
	list_display = ['day', 'breakfast', 'lunch', 'dinner']
	list_filter = ['day', 'breakfast', 'lunch', 'dinner']
	search_fields = ['day', 'breakfast', 'lunch', 'dinner']
	list_per_page = 10


@admin.register(MessAttendance)
class MessAttendanceAdmin(admin.ModelAdmin):
	list_display = ['meal', 'student', 'timestamp']
	list_filter = ['meal', 'student', 'timestamp']
	search_fields = ['meal', 'student', 'timestamp']


@admin.register(MessBill)
class MessBillAdmin(admin.ModelAdmin):
	list_display = ['amount', 'month', 'paid']
	list_filter = ['amount', 'month', 'paid']
	search_fields = ['amount', 'month', 'paid']




@admin.register(Messsettings)
class MesssettingsAdmin(admin.ModelAdmin):
	list_display = ['display_name']
	readonly_fields = ['hostel']
	list_per_page = 10

	def display_name(self, obj):
		return "Messsettings"
	display_name.short_description = "Name"


	def get_queryset(self, request):
		qs = super().get_queryset(request)
		# superuser still sees everything
		if request.user.is_superuser:
			return qs

		# if you’ve ensured each user is in exactly one Django Group:
		hostel = Hostel.objects.filter(mess_sec = request.user).first()
		if not hostel:
			return qs.none()  # no group, no records
		return qs.filter(hostel=hostel)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
	list_display = ['student', 'date']
	list_filter = ['student', 'date']
	search_fields = ['student', 'date']
