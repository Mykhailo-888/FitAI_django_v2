from django.db import models
from django.utils import timezone

class UserData(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)

    # 23 параметри
    age = models.FloatField(null=True, blank=True)
    height_cm = models.FloatField(null=True, blank=True)
    weight_kg = models.FloatField(null=True, blank=True)
    waist_circumference_cm = models.FloatField(null=True, blank=True)
    emotional_stress = models.FloatField(null=True, blank=True)
    alcohol_units_per_week = models.FloatField(null=True, blank=True)
    daily_calories_kcal = models.FloatField(null=True, blank=True)
    max_push_ups = models.FloatField(null=True, blank=True)
    max_pull_ups = models.FloatField(null=True, blank=True)
    run_1km_min = models.FloatField(null=True, blank=True)
    run_100m_sec = models.FloatField(null=True, blank=True)
    cooper_test_km = models.FloatField(null=True, blank=True)
    burpees_3min = models.FloatField(null=True, blank=True)
    push_ups_1min = models.FloatField(null=True, blank=True)
    sleep_hours = models.FloatField(null=True, blank=True)
    resting_heart_rate_bpm = models.FloatField(null=True, blank=True)
    hrv = models.FloatField(null=True, blank=True)
    systolic_blood_pressure_mmhg = models.FloatField(null=True, blank=True)
    mitochondria_placeholder = models.FloatField(null=True, blank=True)
    testosterone_ng_dl = models.FloatField(null=True, blank=True)
    cortisol_ug_dl = models.FloatField(null=True, blank=True)
    hemoglobin_g_dl = models.FloatField(null=True, blank=True)
    crp_mg_l = models.FloatField(null=True, blank=True)

    # Результати
    prediction = models.JSONField(null=True, blank=True)
    weekly_plan = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Data {self.timestamp.date()}"