from django import forms
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from .models import Messcut, MessBill
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
		start_date = self.cleaned_data.get('start_date')
		end_date = self.cleaned_data['end_date']

		if start_date and end_date:
			if end_date < start_date + timedelta(days=1):
				raise ValidationError("The end date must be at least 1 days after the start date.")
			if end_date > start_date + timedelta(days=8):
				raise ValidationError("The end date cannot be more than 8 days after the start date.")
		return end_date

	def clean(self):
		cleaned_data = super().clean()
		start_date = cleaned_data.get('start_date')
		end_date = cleaned_data.get('end_date')

		# Calculate the total days for the current mess cut

		if start_date and end_date:
			# Ensure both dates are in the same month
			if start_date.month != end_date.month or start_date.year != end_date.year:
				raise ValidationError("The start and end dates must be in the same month.")
			if start_date.month != date.today().month or start_date.year != date.today().year:
				raise ValidationError("The start date must be in the current month.")
			current_messcut_days = (end_date - start_date).days + 1

			# Check for overlapping mess cuts
			if self.request:
				applicant = Application.objects.filter(applicant=self.request.user, accepted=True).first()
				if applicant:
					# Get all mess cuts for the current month and year
					existing_messcuts = applicant.messcuts.filter(
						start_date__month=start_date.month,
						start_date__year=start_date.year
					)
					if existing_messcuts:
						total_messcut_days = sum(
							(messcut.end_date - messcut.start_date).days + 1 for messcut in existing_messcuts
						)
						for messcut in existing_messcuts:
							if (start_date <= messcut.end_date and end_date >= messcut.start_date):
								raise ValidationError("The mess cut dates overlap with an existing mess cut.")
						# Ensure the total mess cut days do not exceed 10 days
						if total_messcut_days + current_messcut_days > 8:
							raise ValidationError(
								"The total number of mess cut days for the month cannot exceed 8 days.")

		return cleaned_data


from django import forms
from .models import Messsettings


class MesssettingsForm(forms.ModelForm):
	class Meta:
		model = Messsettings
		fields = [
			'total_days',
			'amount_per_day',
			'establishment_charges',
			'feast_charges',
			'other_charges',
			'month_for_bill_calculation',
			'last_date_for_payment',
			'per_day_fine_after_due_date',
		]
		widgets = {
			'month_for_bill_calculation': forms.DateInput(attrs={'type': 'date'}),
			'last_date_for_payment'     : forms.DateInput(attrs={'type': 'date'}),
		}


class PayMessBillForm(forms.ModelForm):
	class Meta:
		model = MessBill
		fields = ['screenshot', 'amount_paid']
		widgets = {
			'screenshot' : forms.ClearableFileInput(attrs={'class': 'form-control'}),
			'amount_paid': forms.NumberInput(attrs={'class': 'form-control'}),
		}
