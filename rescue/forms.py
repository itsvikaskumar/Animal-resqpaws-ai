from django import forms
from .models import RescueReport

class RescueReportForm(forms.ModelForm):
    class Meta:
        model = RescueReport
        fields = [
            'image',
            'species',
            'latitude',
            'longitude',
            'location_address',
            'landmark_notes',
            'reporter_name',
            'reporter_phone',
        ]
        widgets = {
            'species': forms.Select(attrs={'class': 'form-select form-select-lg shadow-sm'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_latitude', 'step': '0.000001', 'readonly': 'readonly'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_longitude', 'step': '0.000001', 'readonly': 'readonly'}),
            'location_address': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_location_address', 'placeholder': 'Detecting street/neighborhood via GPS...'}),
            'landmark_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'e.g. In front of metro pillar #42, animal is sheltering under a tree...'}),
            'reporter_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Full Name'}),
            'reporter_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 000-0000'}),
        }
