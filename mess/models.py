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

    day = models.CharField(max_length=9, choices=DAYS_OF_WEEK, unique=True,blank=True, null=True)
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
    student = models.ForeignKey('application.Application', on_delete=models.CASCADE,blank=True, null=True)
    class Meta:
        unique_together = ('meal', 'student','date')
        ordering = ['timestamp']

    def save(self, *args, **kwargs):
        # Get the current local time
        current_time = timezone.localtime().time()

        # Define meal times (local time)
        breakfast_time = (time(8, 0), time(10, 0))  # Breakfast is served from 8 AM to 10 AM
        lunch_time = (time(12, 10), time(14, 45))    # Lunch is served from 12:10 PM to 12:45 PM
        dinner_time = (time(20, 0), time(21, 0))   # Dinner is served from 8 PM to 9 PM

        # Set meal based on current local time
        if breakfast_time[0] <= current_time < breakfast_time[1]:
            self.meal = 'breakfast'
        elif lunch_time[0] <= current_time < lunch_time[1]:
            self.meal = 'lunch'
        elif dinner_time[0] <= current_time < dinner_time[1]:
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
    amount = models.IntegerField()
    month = models.DateField()
    date_paid = models.DateField(null=True, blank=True)
    paid = models.BooleanField(default=False)
    mess_cut = models.ManyToManyField(Messcut, blank=True)
    def __str__(self):
        return f"{self.amount}"