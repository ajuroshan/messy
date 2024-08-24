from django import forms
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from .models import Messcut
from application.models import Application


class MesscutForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None)
		super().__init__(*args, **kwargs)

	class Meta:
		model = Messcut
		fields = ['start_date', 'end_date']
		widgets = {
			'start_date': forms.DateInput(attrs={'type': 'date'}),
			'end_date'  : forms.DateInput(attrs={'type': 'date'}),
		}

	def clean_start_date(self):
		start_date = self.cleaned_data['start_date']
		if start_date <= date.today():
			raise ValidationError("The start date cannot be today or in the past.")
		return start_date

	def clean_end_date(self):
		end_date = self.cleaned_data['end_date']
		return end_date

	def clean(self):
		cleaned_data = super().clean()
		start_date = cleaned_data.get('start_date')
		end_date = cleaned_data.get('end_date')

		if start_date and end_date:
			# Ensure both dates are in the same month
			if start_date.month != end_date.month or start_date.year != end_date.year:
				raise ValidationError("The start and end dates must be in the same month.")

			# Check for overlapping mess cuts
			if self.request:
				applicant = Application.objects.filter(applicant=self.request.user, accepted=True).first()
				if applicant:
					existing_messcuts = applicant.messcuts.all()
					for messcut in existing_messcuts:
						if (start_date <= messcut.end_date and end_date >= messcut.start_date):
							raise ValidationError("The mess cut dates overlap with an existing mess cut.")

		return cleaned_data

