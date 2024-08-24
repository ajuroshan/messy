from django.contrib import admin

# Register your models here.
from .models import *

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
	list_display = ['applicant','department','semester','mess_no','accepted','created_at']
	list_filter = ['applicant','hostel','mess_no','accepted','created_at']
	search_fields = ['applicant','hostel','accepted','created_at']


@admin.register(AcceptedApplication)
class AcceptedApplicationAdmin(admin.ModelAdmin):
	list_display = ['applicant','department','semester','mess_no','accepted','created_at']
	list_filter = ['applicant','hostel','mess_no','accepted','created_at']
	search_fields = ['applicant','hostel','accepted','created_at']
	list_per_page = 10

	def get_queryset(self, request):
		return Application.objects.filter(accepted=True).order_by("-created_at")

