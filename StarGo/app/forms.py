from django import forms
from .models import *

from django.forms import ModelForm, SplitDateTimeField
from django.forms.widgets import Textarea, TextInput, SplitDateTimeWidget
from django.core.exceptions import ValidationError

class CelebritiesForm(ModelForm):
    class Meta:
        model = Celebrities
        fields = ['firstname', 'lastname', 'nickname', 'groups', 'imageurl']
        widgets = {
            'firstname': TextInput(attrs={'class': 'form-control bg-light'}),
            'lastname': TextInput(attrs={'class': 'form-control bg-light'}),
            'nickname': TextInput(attrs={'class': 'form-control bg-light'}),
            'groups': forms.SelectMultiple(attrs={'class': 'form-control bg-light'}),
            'imageurl': forms.FileInput(attrs={'class': 'form-control bg-light', 'id': 'imageupload'}),
        }

    def clean_data(self):
        cleaned_data = super().clean()
        # Perform custom validation here if needed
        return cleaned_data
    

