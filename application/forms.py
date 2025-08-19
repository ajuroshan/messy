from django import forms
from .models import Application
from django.core.exceptions import ValidationError


class ApplicationForm(forms.ModelForm):
	class Meta:
		model = Application
		fields = ['first_name', 'last_name','student_id','phone_number', 'hostel', 'department', 'semester', 'outmess', 'food_preference','profile_pic']
		widgets = {
			'profile_pic': forms.ClearableFileInput(attrs={'class': 'form-control', 'required': 'required'}),
		}

		def clean_profile_pic(self):
			profile_pic = self.cleaned_data.get('profile_pic')
			print("profile_pic")
			print(profile_pic)

			if profile_pic:
				# Validate the file extension
				valid_extensions = ['png', 'jpg', 'jpeg']
				extension = profile_pic.name.split('.')[-1].lower()
				if extension not in valid_extensions:
					raise ValidationError('Only .png, .jpg, and .jpeg files are allowed.')

				return profile_pic
