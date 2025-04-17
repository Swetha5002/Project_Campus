from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import User, Class
import json

class PaperCodeForm(forms.Form):
    paper_code = forms.CharField(max_length=10, required=True)

class UserForm(forms.ModelForm):
    coding_platform_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Platform Name (e.g., LeetCode)'})
    )
    coding_platform_link = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'placeholder': 'Platform Link (e.g., https://leetcode.com/user)'})
    )

    class_field = forms.ModelChoiceField(
        queryset=Class.objects.all(),
        required=True,
        label="Class",
        help_text="Select the class for the user."
    )

    class Meta:
        model = User
        fields = [
            'profile_image', 'username', 'email', 'name', 'university_number', 
            'batch_year', 'section', 'date_of_birth', 'phone_number', 'gender', 
            'cgpa', 'average_percentage', 'linkedin_link', 'code_platforms'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        name = self.cleaned_data.get('coding_platform_name')
        link = self.cleaned_data.get('coding_platform_link')
        if name and link:
            instance.code_platforms.append({'name': name, 'link': link})
        if commit:
            instance.save()
        return instance


