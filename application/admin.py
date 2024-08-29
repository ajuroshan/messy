from django.contrib import admin

# Register your models here.
from .models import *


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
	list_display = ['get_applicant_name', 'department', 'semester', 'mess_no', 'accepted', 'created_at']
	list_filter = ['applicant__first_name', 'applicant__last_name', 'hostel', 'mess_no', 'accepted', 'created_at']
	search_fields = ['applicant__first_name', 'applicant__last_name', 'hostel', 'accepted', 'created_at']
	actions = ['accept_application', 'cancel_application']

	def get_applicant_name(self, obj):
		return f"{obj.applicant.first_name} {obj.applicant.last_name}"

	get_applicant_name.short_description = 'Applicant Full Name'

	def accept_application(self, request, queryset):
		"""
		Mark selected applications as verified.
		"""
		updated_count = queryset.update(accepted=True)
		self.message_user(request, f"{updated_count} applications were successfully marked as verified.")

	accept_application.short_description = "Accept selected Applications"

	def cancel_application(self, request, queryset):
		"""
		Mark selected applications as verified.
		"""
		updated_count = queryset.update(accepted=False)
		self.message_user(request, f"{updated_count} applications were successfully marked as verified.")

	cancel_application.short_description = "Cancel selected Applications"


@admin.register(AcceptedApplication)
class AcceptedApplicationAdmin(admin.ModelAdmin):
	list_display = ['get_applicant_name', 'department', 'semester', 'mess_no', 'accepted', 'created_at']
	list_filter = ['applicant', 'hostel', 'mess_no', 'accepted', 'created_at']
	search_fields = ['applicant', 'hostel', 'accepted', 'created_at']
	actions = ['accept_application', 'cancel_application', 'make_official_outmess']

	def get_applicant_name(self, obj):
		return f"{obj.applicant.first_name} {obj.applicant.last_name}"

	get_applicant_name.short_description = 'Applicant Full Name'

	def accept_application(self, request, queryset):
		"""
		Mark selected applications as verified.
		"""
		updated_count = queryset.update(accepted=True)
		self.message_user(request, f"{updated_count} applications were successfully marked as verified.")

	accept_application.short_description = "Accept selected applications"

	def cancel_application(self, request, queryset):
		"""
		Mark selected applications as verified.
		"""
		updated_count = queryset.update(accepted=False)
		self.message_user(request, f"{updated_count} applications were successfully marked as verified.")

	cancel_application.short_description = "Cancel selected applications"

	def make_official_outmess(self, request, queryset):
		"""
		Mark selected applications as verified.
		"""
		updated_count = queryset.update(official_outmess=True)
		self.message_user(request, f"{updated_count} applications were successfully marked as verified.")

	make_official_outmess.short_description = "Mark students as official outmess"

	def get_queryset(self, request):
		return Application.objects.filter(accepted=True).order_by("-created_at")
