from django import forms
from .models import UserData

class UpdateDataForm(forms.ModelForm):
    class Meta:
        model = UserData
        fields = [
            'age', 'height_cm', 'weight_kg', 'waist_circumference_cm', 'emotional_stress',
            'alcohol_units_per_week', 'daily_calories_kcal',
            'max_push_ups', 'max_pull_ups', 'run_1km_min', 'run_100m_sec',
            'cooper_test_km', 'burpees_3min', 'push_ups_1min', 'sleep_hours',
            'resting_heart_rate_bpm', 'systolic_blood_pressure_mmhg',
            'mitochondria_placeholder', 'testosterone_ng_dl', 'cortisol_ug_dl',
            'hemoglobin_g_dl', 'crp_mg_l', 'hrv'
        ]
        labels = {field: field.replace('_', ' ').title() for field in fields}
        widgets = {
            field: forms.NumberInput(attrs={'step': '0.1', 'placeholder': 'Leave blank for default'})
            for field in fields
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = False  # всі поля необов’язкові