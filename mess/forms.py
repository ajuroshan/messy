import datetime
import json
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from .models import Messcut, MessBill, Feedback, MessClosedDate
from application.models import Application
from .models import Messsettings
from django import forms


class MesscutForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Messcut
        fields = ["start_date", "end_date"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_start_date(self):
        start_date = self.cleaned_data["start_date"]
        if start_date <= date.today():
            raise ValidationError("The start date cannot be today or in the past.")
        return start_date

    def clean_end_date(self):
        start_date = self.cleaned_data.get("start_date")
        end_date = self.cleaned_data["end_date"]
        hostel_code = Application.objects.filter(applicant=self.request.user, accepted=True).first().hostel.code

        
        if hostel_code == 'SNT':
            snt_min_days = 4
            gap = (end_date - start_date).days + 1    # difference in days
            if gap < snt_min_days:
                raise ValidationError(
                    f"You should have at least {snt_min_days} days gap between two mess cuts."
                )

        if start_date and end_date:
            if end_date < start_date + timedelta(days=1):
                raise ValidationError(
                    "The end date must be at least 1 days after the start date."
                )
            if hostel_code == 'SNT' or hostel_code == 'SWR':
                if end_date > start_date + timedelta(days=10):
                    raise ValidationError(
                        "The end date cannot be more than 10 days after the start date."
                    )
            else:
                if end_date > start_date + timedelta(days=8):
                    raise ValidationError(
                        "The end date cannot be more than 8 days after the start date."
                    )
        return end_date

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        hostel_code = Application.objects.filter(applicant=self.request.user, accepted=True).first().hostel.code

        # Calculate the total days for the current mess cut

        if start_date and end_date:
            # Ensure both dates are in the same month
            if start_date.month != end_date.month or start_date.year != end_date.year:
                raise ValidationError(
                    "The start and end dates must be in the same month."
                )
            # if start_date.month != date.today().month or start_date.year != date.today().year:
            # 	raise ValidationError("The start date must be in the current month.")
            current_messcut_days = (end_date - start_date).days + 1

            # Check for overlapping mess cuts
            if self.request:
                applicant = Application.objects.filter(
                    applicant=self.request.user, accepted=True
                ).first()
                if applicant:
                    # Get all mess cuts for the current month and year
                    existing_messcuts = applicant.messcuts.filter(
                        start_date__month=start_date.month,
                        start_date__year=start_date.year,
                    )
                    if existing_messcuts:
                        total_messcut_days = sum(
                            (messcut.end_date - messcut.start_date).days + 1
                            for messcut in existing_messcuts
                        )
                        for messcut in existing_messcuts:
                            if (
                                start_date <= messcut.end_date
                                and end_date >= messcut.start_date
                            ):
                                raise ValidationError(
                                    "The mess cut dates overlap with an existing mess cut."
                                )
                        # Ensure the total mess cut days do not exceed 10 days

                        if hostel_code == 'SNT' or hostel_code == 'SWR':
                            if total_messcut_days + current_messcut_days > 10:
                                raise ValidationError(
                                    "The total number of mess cut days for the month cannot exceed 10 days."
                                )
                        else:
                            if total_messcut_days + current_messcut_days > 8:
                                raise ValidationError(
                                    "The total number of mess cut days for the month cannot exceed 8 days."
                                )

        return cleaned_data


class MesssettingsForm(forms.ModelForm):
    mess_closed_dates = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "multi-date-picker",
                "placeholder": "Select multiple dates",
            }
        ),
        label="Mess Closed Dates",
    )

    class Meta:
        model = Messsettings
        fields = [
            "total_days",
            "amount_per_day",
            "establishment_charges",
            "feast_charges",
            "other_charges",
            "month_for_bill_calculation",
            "last_date_for_payment",
            "per_day_fine_after_due_date",
            "mess_closed_dates",
        ]
        widgets = {
            "month_for_bill_calculation": forms.DateInput(attrs={"type": "date"}),
            "bill_calculation_date": forms.DateInput(attrs={"type": "date"}),
            "last_date_for_payment": forms.DateInput(attrs={"type": "date"}),
        }
        labels = {
            "month_for_bill_calculation": "Bill Date",
        }

    def clean_mess_closed_dates(self):
        """Validate the JSON input and ensure dates are in the correct format."""
        data = self.cleaned_data.get("mess_closed_dates", "")
        if data:
            try:
                # Attempt to parse as JSON directly
                dates = json.loads(data)
                if not isinstance(dates, list):
                    raise forms.ValidationError("Please provide a list of dates.")
                # Validate each date
                for date in dates:
                    datetime.datetime.strptime(
                        date, "%Y-%m-%d"
                    )  # Ensure valid date format
                return dates
            except (ValueError, json.JSONDecodeError):
                raise forms.ValidationError(
                    "Please enter valid JSON (e.g., ['2024-11-01', '2024-11-02'])."
                )
        return []

    def save(self, commit=True):
        """Save the parsed dates into the related MessClosedDate model."""
        instance = super().save(commit=False)
        dates = self.cleaned_data.get("mess_closed_dates", [])

        if commit:
            instance.save()

            # Clear old dates and create new ones
            instance.mess_closed_dates.clear()
            for date_str in dates:
                date_obj, created = MessClosedDate.objects.get_or_create(date=date_str)
                instance.mess_closed_dates.add(date_obj)

        return instance


class PayMessBillForm(forms.ModelForm):
    class Meta:
        model = MessBill
        fields = ["screenshot", "amount_paid"]
        widgets = {
            "screenshot": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "amount_paid": forms.NumberInput(attrs={"class": "form-control"}),
        }


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["feedback"]
        widgets = {
            "feedback": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
        }
