from django.db import models
from django.contrib.auth.models import User
from mess.models import *

# Create your models here.

hostels = [
	('Sagar', 'Sagar'),

]

departments = [
	('cse', 'CSE'),
	('ece', 'ECE'),
	('mech', 'MECH'),
	('civil', 'CIVIL'),
	('eee', 'EEE'),
	('it', 'IT'),
	('saftey', 'SAFTEY'),
	('mtech', 'MTECH'),
	('main_campus', 'MAIN CAMPUS'),
]

food_preferences = [
	('veg', 'Veg'),
	('nonveg', 'Non-Veg'),
]

semester_choices = [
	('S1', 'S1'),
	('S2', 'S2'),
	('S3', 'S3'),
	('S4', 'S4'),
	('S5', 'S5'),
	('S6', 'S6'),
	('S7', 'S7'),
	('S8', 'S8'),


]

class Application(models.Model):
	applicant = models.ForeignKey('auth.User', on_delete=models.CASCADE)
	mess_no = models.IntegerField(default=100)
	hostel = models.CharField(max_length=100, choices=hostels, default='Sagar')
	accepted = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	messcuts = models.ManyToManyField(Messcut, blank=True)
	department = models.CharField(max_length=100, choices=departments, default='')
	semester = models.CharField(max_length=100, choices=semester_choices, default='')
	outmess = models.BooleanField(default=False)
	food_preference = models.CharField(max_length=100, choices=food_preferences, default='nonveg')
	claim = models.BooleanField(default=False)


	def __str__(self):
		return str(self.applicant.username + ' - ' + self.created_at.strftime('%d-%m-%Y'))


class AcceptedApplication(Application):
    class Meta:
        proxy = True