from django import forms
from .models import *

from django.forms import ModelForm, SplitDateTimeField
from django.forms.widgets import Textarea, TextInput, SplitDateTimeWidget
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

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
    

class PlacesForm(ModelForm):
    class Meta:
        model = Places
        fields = ['name', 'googlemaplink', 'address', 'imageurl']
        widgets = {
            'name': TextInput(attrs={'class': 'form-control bg-light'}),
            'googlemaplink': TextInput(attrs={'class': 'form-control bg-light'}),
            'address': Textarea(attrs={'class': 'form-control bg-light'}),
            'imageurl': forms.FileInput(attrs={'class': 'form-control bg-light', 'id': 'imageupload'}),
        }

    def clean_data(self):
        cleaned_data = super().clean()
        # Perform custom validation here if needed
        return cleaned_data


class SightingsForm(ModelForm):
    class Meta:
        model = Sightings
        fields = ['places', 'arrivaldate']
        # add-fields ==> ['celebrities', 'places', 'arrivaldate', 'addby_users', 'created_at']
        widgets = {
            'places': forms.Select(attrs={'class': 'form-control bg-light'}),
            'arrivaldate': forms.DateInput(attrs={'class': 'form-control bg-light', 'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        # Perform custom validation here if needed
        return cleaned_data
    

class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label='Password', 
        widget=forms.PasswordInput(attrs={'class': 'form-control bg-light'})
    )
    password2 = forms.CharField(
        label='Password confirmation', 
        widget=forms.PasswordInput(attrs={'class': 'form-control bg-light'})
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name")
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control bg-light'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control bg-light'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control bg-light'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        # Perform custom validation here if needed
        username = cleaned_data.get("username")
        if username and username.lower() == "admin":
            # ถ้าเงื่อนไขผิด ให้ raise ValidationError
            raise forms.ValidationError("Username 'admin' is not allowed.")
        return cleaned_data
