from django.contrib import admin

# Register your models here.
from .models import Patient, DiaHealthRecord

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("patient_code", "last_name", "first_name", "gender", "age", "created_at")
    search_fields = ("patient_code", "last_name", "first_name")

@admin.register(DiaHealthRecord)
class DiaHealthRecordAdmin(admin.ModelAdmin):
    list_display = ("patient", "age", "gender", "bmi", "glucose", "diabetic", "created_at")
    list_filter = ("diabetic", "gender")
    search_fields = ("patient__patient_code",)
