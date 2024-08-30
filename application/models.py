from django.db import models
from django.contrib.auth.models import User
from mess.models import *
import qrcode
from io import BytesIO
from django.core.files import File

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
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100, blank=True, null=True)
	mess_no = models.IntegerField(default=100)
	hostel = models.CharField(max_length=100, choices=hostels, default='Sagar')
	accepted = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	messcuts = models.ManyToManyField(Messcut, blank=True,related_name='application')
	department = models.CharField(max_length=100, choices=departments, default='')
	semester = models.CharField(max_length=100, choices=semester_choices, default='')
	outmess = models.BooleanField(default=False)
	food_preference = models.CharField(max_length=100, choices=food_preferences, default='nonveg')
	claim = models.BooleanField(default=False)
	qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
	attendance = models.ManyToManyField(MessAttendance, blank=True)
	mess_bill = models.ManyToManyField(MessBill, blank=True,related_name='application')
	profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

	official_outmess = models.BooleanField(default=False)

	def __str__(self):
		return str(self.applicant.username + ' - ' + str(self.mess_no))

	def save(self, *args, **kwargs):
		if not self.pk:  # Only generate a QR code for new applications
			last_application = Application.objects.order_by('mess_no').last()
			if last_application:
				self.mess_no = last_application.mess_no + 1
			else:
				self.mess_no = 100

			qr = qrcode.QRCode(
				version=1,
				error_correction=qrcode.constants.ERROR_CORRECT_L,
				box_size=10,
				border=4,
			)
			qr.add_data(str(self.mess_no))  # Use application ID or another unique identifier
			qr.make(fit=True)

			img = qr.make_image(fill='black', back_color='white')
			img_io = BytesIO()
			img.save(img_io, format='PNG')
			img_file = File(img_io, name=f'{self.mess_no}.png')

			self.qr_code.save(f'{self.mess_no}.png', img_file, save=False)

		super().save(*args, **kwargs)




class AcceptedApplication(Application):
	class Meta:
		proxy = True


class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	profile_pic = models.URLField(max_length=200, blank=True, null=True)
