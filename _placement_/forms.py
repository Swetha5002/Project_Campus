from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import User, Section

class PaperCodeForm(forms.Form):
    paper_code = forms.CharField(max_length=10, required=True)

class UserForm(UserCreationForm):  # Inherit from UserCreationForm
    section = forms.ModelChoiceField(
        queryset=Section.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Select section'
        }),
        required=True
    )

    class Meta:
        model = User
        fields = [
            'username', 
            'name', 
            'email', 
            'batch', 
            'section', 
            'profile_image',
            'university_number', 
            'date_of_birth', 
            'phone_number', 
            'gender',
            'password1',  # Add password1
            'password2',  # Add password2
        ]
        widgets = {
            'batch': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select batch'
            }),
            'university_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter university number'
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control', 
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
            'gender': forms.Select(attrs={
                'class': 'form-control', 
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'batch' in self.data:
            try:
                batch_id = int(self.data.get('batch'))
                self.fields['section'].queryset = Section.objects.filter(batch_id=batch_id).order_by('name')
            except (ValueError, TypeError):
                self.fields['section'].queryset = Section.objects.none()
        elif self.instance.pk and self.instance.batch:
            self.fields['section'].queryset = Section.objects.filter(batch=self.instance.batch).order_by('name')

