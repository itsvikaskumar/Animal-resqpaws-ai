from django import forms
from django.contrib.auth.models import User
from .models import EmergencyReport

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create strong password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Gmail / Email Address'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

class EmergencyReportDirectForm(forms.ModelForm):
    class Meta:
        model = EmergencyReport
        fields = ['reporter_name', 'reporter_phone', 'reporter_email', 'address_text', 'image']
        widgets = {
            'reporter_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Full Name'}),
            'reporter_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number (for SMS updates)'}),
            'reporter_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Gmail Address'}),
            'address_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Landmark / Location details'}),
        }