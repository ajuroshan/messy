from django.contrib import admin
from .models import *
from django.contrib import admin
from django.urls import path
from django.http import HttpResponseRedirect
from .views import mess_bill_admin
from django.utils.html import format_html


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

	# Override the changelist view to add a custom link
	def changelist_view(self, request, extra_context=None):
		extra_context = extra_context or {}
		extra_context['custom_link'] = format_html(
			'<a class="button" href="{}">Custom Mess Bill Page</a>', '/admin/mess-bill-admin/'
		)
		return super().changelist_view(request, extra_context=extra_context)

	# You can add custom URLs for your custom views
	def get_urls(self):
		urls = super().get_urls()
		custom_urls = [
			path('mess-bill-admin/', self.admin_site.admin_view(mess_bill_admin), name='mess_bill_admin'),
		]
		return custom_urls + urls


@admin.register(Messsettings)
class MesssettingsAdmin(admin.ModelAdmin):
	list_display = ['total_days', 'amount_per_day', 'establishment_charges', 'feast_charges', 'other_charges']
	list_filter = ['total_days', 'amount_per_day', 'establishment_charges', 'feast_charges', 'other_charges']
	search_fields = ['total_days', 'amount_per_day', 'establishment_charges', 'feast_charges', 'other_charges']
	list_per_page = 10

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
	list_display = ['student', 'date']
	list_filter = ['student', 'date']
	search_fields = ['student', 'date']
