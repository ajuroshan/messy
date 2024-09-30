import datetime

from django.utils import timezone
from datetime import time

from django.db import models


# Create your models here.

class Messcut(models.Model):
	start_date = models.DateField()
	end_date = models.DateField()

	def __str__(self):
		return f"Messcut from {self.start_date} to {self.end_date}"


class Messmenu(models.Model):
	DAYS_OF_WEEK = [
		('monday', 'Monday'),
		('tuesday', 'Tuesday'),
		('wednesday', 'Wednesday'),
		('thursday', 'Thursday'),
		('friday', 'Friday'),
		('saturday', 'Saturday'),
		('sunday', 'Sunday'),
	]

	day = models.CharField(max_length=9, choices=DAYS_OF_WEEK, unique=True, blank=True, null=True)
	breakfast = models.CharField(max_length=255)
	lunch = models.CharField(max_length=255)
	dinner = models.CharField(max_length=255)

	class Meta:
		unique_together = ('day',)

	def __str__(self):
		return f"{self.day.capitalize()}: Breakfast - {self.breakfast}, Lunch - {self.lunch}, Dinner - {self.dinner}"


class MessAttendance(models.Model):
	MEAL_CHOICES = [
		('breakfast', 'Breakfast'),
		('lunch', 'Lunch'),
		('dinner', 'Dinner'),
	]
	date = models.DateField(auto_now_add=True)
	meal = models.CharField(max_length=10, choices=MEAL_CHOICES)
	timestamp = models.DateTimeField(auto_now_add=True)
	student = models.ForeignKey('application.Application', on_delete=models.CASCADE, blank=True, null=True)

	class Meta:
		unique_together = ('meal', 'student', 'date')
		ordering = ['timestamp']

	def save(self, *args, **kwargs):
		# Get the current local time
		current_time = timezone.localtime().time()

		# Fetch meal times from Messsettings
		mess_settings = Messsettings.objects.first()

		# Set meal based on current local time
		if mess_settings.breakfast_start_time <= current_time < mess_settings.breakfast_end_time:
			self.meal = 'breakfast'
		elif mess_settings.lunch_start_time <= current_time < mess_settings.lunch_end_time:
			self.meal = 'lunch'
		elif mess_settings.dinner_start_time <= current_time < mess_settings.dinner_end_time:
			self.meal = 'dinner'
		else:
			raise ValueError("Meal time does not match any defined meal period")

		super().save(*args, **kwargs)

	def __str__(self):
		return f"{self.timestamp} - {self.meal}"


class MessBill(models.Model):
	total_days = models.IntegerField(default=30)
	effective_days = models.IntegerField(default=0)
	amount_per_day = models.IntegerField(default=10)
	establishment_charges = models.IntegerField(default=50)
	feast_charges = models.IntegerField(default=0)
	other_charges = models.IntegerField(default=0)
	mess_cuts = models.IntegerField(default=0)
	amount = models.IntegerField(default=0)
	month = models.DateField()

	date_paid = models.DateField(null=True, blank=True)
	paid = models.BooleanField(default=False)
	screenshot = models.ImageField(upload_to='payment_screenshots', blank=True, null=True)
	fine_paid = models.IntegerField(default=0)
	amount_paid = models.IntegerField(default=0)

	def __str__(self):
		return f"{self.amount}"


class Feedback(models.Model):
	student = models.ForeignKey('application.Application', on_delete=models.CASCADE)
	feedback = models.TextField()
	date = models.DateField(auto_now_add=True)

	def __str__(self):
		return f"{self.student.first_name} - {self.date}"

class Messsettings(models.Model):
	total_days = models.IntegerField(default=30)
	amount_per_day = models.IntegerField(default=10)
	establishment_charges = models.IntegerField(default=50)
	feast_charges = models.IntegerField(default=0)
	other_charges = models.IntegerField(default=0)
	mess_secretary_upi_id = models.CharField(max_length=255)
	mess_secretary_upi_id_link = models.CharField(max_length=255)
	sagar_post_metric_upi_id = models.CharField(max_length=255)
	sagar_post_metric_upi_id_link = models.CharField(max_length=255)
	mess_secretary_upi_qr = models.ImageField(upload_to='upi_qr_codes', blank=True, null=True)
	sagar_post_metric_upi_qr = models.ImageField(upload_to='upi_qr_codes', blank=True, null=True)
	month_for_bill_calculation = models.DateField()
	last_date_for_payment = models.DateField()
	per_day_fine_after_due_date = models.IntegerField(default=0)
	mess_secretary_name = models.CharField(max_length=10)
	mess_secretary_contact = models.CharField(max_length=10)
	assistant_mess_secretary_name = models.CharField(max_length=10)
	assistant_mess_secretary_contact = models.CharField(max_length=10)
	publish_mess_bill = models.BooleanField(default=False)

	breakfast_start_time = models.TimeField()
	breakfast_end_time = models.TimeField()

	lunch_start_time = models.TimeField()
	lunch_end_time = models.TimeField()

	dinner_start_time = models.TimeField()
	dinner_end_time = models.TimeField()

	messcut_closing_time = models.TimeField()

	mess_closed_days = models.IntegerField(default=0)

	bill_calculation_date = models.DateField(default=datetime.date.today())



	def __str__(self):
		return f"{self.total_days} days, {self.amount_per_day} per day"
