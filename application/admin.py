from django.contrib import admin
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Group

# Register your models here.
from .models import *


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
	list_display = ['get_applicant_name', 'department', 'semester', 'mess_no', 'accepted','claim','outmess','official_outmess', 'created_at']
	list_filter = ['applicant__first_name', 'applicant__last_name', 'hostel', 'mess_no', 'accepted', 'created_at']
	search_fields = ['applicant__first_name', 'applicant__last_name','mess_no', 'created_at']
	actions = ['accept_application', 'cancel_application', 'make_official_outmess', 'make_mess_assistant',
	           'dismiss_mess_assistant']

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

	def make_mess_assistant(self, request, queryset):
		"""
		Mark selected applications as mess_assistants.
		"""
		# Get or create the mess_assistants group
		mess_assistants_group, created = Group.objects.get_or_create(name='mess_assistants')

		# Iterate over the selected applications
		for application in queryset:
			# Fetch the applicant user from the application
			user = application.applicant

			# Add the user to the mess_assistants group
			if not user.groups.filter(name='mess_assistants').exists():
				user.groups.add(mess_assistants_group)
				self.message_user(request, f'User {user.username} added to mess_assistants group.')
			else:
				self.message_user(request, f'User {user.username} is already a mess_assistant.')

		# Optionally, you might want to refresh the changelist view
		return HttpResponseRedirect(request.get_full_path())

	make_mess_assistant.short_description = "Make selected applications mess assistants"

	def dismiss_mess_assistant(self, request, queryset):
		"""
		Dismiss selected applications as mess_assistants.
		"""
		# Get or create the mess_assistants group
		mess_assistants_group, created = Group.objects.get_or_create(name='mess_assistants')

		# Iterate over the selected applications
		for application in queryset:
			# Fetch the applicant user from the application
			user = application.applicant

			# Add the user to the mess_assistants group
			if user.groups.filter(name='mess_assistants').exists():
				user.groups.remove(mess_assistants_group)
				self.message_user(request, f'User {user.username} removed from mess_assistants group.')
			else:
				self.message_user(request, f'User {user.username} is not a mess_assistant.')

		# Optionally, you might want to refresh the changelist view
		return HttpResponseRedirect(request.get_full_path())

	dismiss_mess_assistant.short_description = "Dismiss selected mess assistants"


@admin.register(AcceptedApplication)
class AcceptedApplicationAdmin(admin.ModelAdmin):
	list_display = ['get_applicant_name', 'department', 'semester', 'mess_no', 'accepted','claim','outmess','official_outmess', 'created_at']
	list_filter = ['applicant', 'hostel', 'mess_no', 'accepted', 'created_at']
	search_fields = ['applicant__first_name', 'applicant__last_name','mess_no', 'created_at']
	actions = ['accept_application', 'cancel_application', 'make_official_outmess', 'make_mess_assistant',
	           'dismiss_mess_assistant','make_claim','cancel_claim','make_outmess','cancel_outmess']

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

	# add to mess_assistants group
	def make_mess_assistant(self, request, queryset):
		"""
		Mark selected applications as mess_assistants.
		"""
		# Get or create the mess_assistants group
		mess_assistants_group, created = Group.objects.get_or_create(name='mess_assistants')

		# Iterate over the selected applications
		for application in queryset:
			# Fetch the applicant user from the application
			user = application.applicant

			# Add the user to the mess_assistants group
			if not user.groups.filter(name='mess_assistants').exists():
				user.groups.add(mess_assistants_group)
				self.message_user(request, f'User {user.username} added to mess_assistants group.')
			else:
				self.message_user(request, f'User {user.username} is already a mess_assistant.')

		# Optionally, you might want to refresh the changelist view
		return HttpResponseRedirect(request.get_full_path())

	make_mess_assistant.short_description = "Make selected applications mess assistants"

	def dismiss_mess_assistant(self, request, queryset):
		"""
		Dismiss selected applications as mess_assistants.
		"""
		# Get or create the mess_assistants group
		mess_assistants_group, created = Group.objects.get_or_create(name='mess_assistants')

		# Iterate over the selected applications
		for application in queryset:
			# Fetch the applicant user from the application
			user = application.applicant

			# Add the user to the mess_assistants group
			if user.groups.filter(name='mess_assistants').exists():
				user.groups.remove(mess_assistants_group)
				self.message_user(request, f'User {user.username} removed from mess_assistants group.')
			else:
				self.message_user(request, f'User {user.username} is not a mess_assistant.')

		# Optionally, you might want to refresh the changelist view
		return HttpResponseRedirect(request.get_full_path())

	dismiss_mess_assistant.short_description = "Dismiss selected mess assistants"



	def make_claim(self, request, queryset):
		"""
		Mark selected applications as verified.
		"""
		updated_count = queryset.update(claim=True)
		self.message_user(request, f"{updated_count} applications were successfully marked as verified.")

	make_claim.short_description = "Mark selected applications have claim"

	def cancel_claim(self, request, queryset):
		"""
		Mark selected applications as verified.
		"""
		updated_count = queryset.update(claim=False)
		self.message_user(request, f"{updated_count} applications were successfully marked as verified.")

	cancel_claim.short_description = "Cancel claim of selected applications"


	def make_outmess(self, request, queryset):
		"""
		Mark selected applications as verified.
		"""
		updated_count = queryset.update(outmess=True)
		self.message_user(request, f"{updated_count} applications were successfully marked as verified.")

	make_outmess.short_description = "Mark selected applications as Outmess"

	def cancel_outmess(self, request, queryset):
		"""
		Mark selected applications as verified.
		"""
		updated_count = queryset.update(outmess=False)
		self.message_user(request, f"{updated_count} applications were successfully marked as verified.")

	cancel_outmess.short_description = "Dismiss selected applications as Outmess"

	def get_queryset(self, request):
		return Application.objects.filter(accepted=True).order_by("-created_at")
