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
    date = models.DateField()
    breakfast = models.TextField()
    lunch = models.TextField()
    dinner = models.TextField()

    def __str__(self):
        return f"Menu for {self.date}"


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
        breakfast_time = (time(6, 0), time(9, 0))  # Breakfast is served from 6 AM to 9 AM
        lunch_time = (time(12, 0), time(14, 0))    # Lunch is served from 12 PM to 2 PM
        dinner_time = (time(19, 0), time(21, 0))   # Dinner is served from 7 PM to 9 PM

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