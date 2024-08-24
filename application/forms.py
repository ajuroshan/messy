from django import forms
from .models import Application

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['hostel', 'department', 'semester', 'outmess', 'food_preference', 'claim']