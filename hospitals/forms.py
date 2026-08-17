from django import forms
from .models import Hospital, Ambulance

class AmbulanceForm(forms.ModelForm):
    class Meta:
        model = Ambulance
        fields = ['vehicle_number', 'driver_name', 'driver_phone', 'paramedic_name', 'status']
        widgets = {
            'vehicle_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. DL-01-AMB-9988'}),
            'driver_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Driver Full Name'}),
            'driver_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 123-4567'}),
            'paramedic_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Paramedic Name (Optional)'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class HospitalForm(forms.ModelForm):
    class Meta:
        model = Hospital
        fields = ['name', 'address', 'city', 'phone', 'emergency_phone', 'email', 'latitude', 'longitude', 'capacity', 'has_24_7_ambulance', 'has_icu']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'has_24_7_ambulance': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_icu': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
