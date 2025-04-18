from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import User
import json

class PaperCodeForm(forms.Form):
    paper_code = forms.CharField(max_length=10, required=True)
from django import forms
from .models import User

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'name', 'email', 'batch', 'section', 'profile_image', 
                 'university_number', 'date_of_birth', 'phone_number', 'gender',
                 'cgpa', 'linkedin_link', 'code_platforms']
        widgets = {
            'university_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter university number'
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control', 
                'label': 'Roll Number',
                'placeholder': 'Enter roll number',
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter email address'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter phone number'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control', 
                'placeholder': 'Select date of birth'
            }),
            'batch_year': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter batch year'
            }),
            'section': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter section'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control', 
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add any custom initialization here
        
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user
